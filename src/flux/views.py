from itertools import chain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from flux.forms import TicketForm, ReviewForm
from flux.models import Ticket, Review, UserFollows

User = get_user_model()

"""Le décorateur login_required garantit que seuls les utilisateurs
 authentifiés peuvent accéder à cette vue."""


@login_required
def flux(request):
    return render(request, 'flux/flux.html')

@login_required
def posts(request):
    tickets = Ticket.objects.filter(user=request.user)
    reviews = Review.objects.filter(user=request.user)

    posts_data = []
    
    for ticket in tickets:
        ticket.is_review = False
        ticket.content = ticket.description
        ticket.image = ticket.image
        posts_data.append(ticket)
        
    for review in reviews:
        review.is_review = True
        review.title = review.headline
        review.content = review.body
        posts_data.append(review)

    posts_data = sorted(posts_data, key=lambda x: x.time_created, reverse=True)

    return render(request, 'flux/posts.html', {'posts': posts_data})

@login_required
def subscriptions(request):
    if request.method == 'POST' and 'username' in request.POST:
        username = request.POST.get('username')
        try:
            user_to_follow = User.objects.get(username=username)
            if user_to_follow == request.user:
                messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
            elif UserFollows.objects.filter(user=request.user, followed_user=user_to_follow).exists():
                messages.warning(request, f"Vous suivez déjà {username}.")
            else:
                UserFollows.objects.create(user=request.user, followed_user=user_to_follow)
                messages.success(request, f"Vous suivez maintenant {username}.")
        except User.DoesNotExist:
            messages.error(request, f"L'utilisateur {username} n'existe pas.")
        return redirect('subscriptions')
    
    # Récupération des utilisateurs suivis
    users_followed = User.objects.filter(
        id__in=UserFollows.objects.filter(user=request.user).values_list('followed_user', flat=True)
    )
    
    # Récupération des abonnés (followers)
    followers = User.objects.filter(
        id__in=UserFollows.objects.filter(followed_user=request.user).values_list('user', flat=True)
    )
    
    context = {
        'users_followed': users_followed,
        'followers': followers,
    }
    return render(request, 'flux/subscriptions.html', context)

@login_required
def create_review(request):
    review_form = ReviewForm()
    ticket_form = TicketForm()
    if request.method == 'POST':
        review_form = ReviewForm(request.POST, request.FILES)
        ticket_form = TicketForm(request.POST, request.FILES)
        if review_form.is_valid() and ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('flux')
    return render(request, 'flux/create_review.html', {
        'review_form': review_form,
        'ticket_form': ticket_form
    })

@login_required
def ask_ticket(request):
    form = TicketForm()
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('flux')
    return render(request, 'flux/ask_ticket.html', {'form': form})

@login_required
def unfollow_user(request, user_id):
    if request.method == 'POST':
        user_to_unfollow = get_object_or_404(User, id=user_id)
        follow_relation = UserFollows.objects.filter(
            user=request.user,
            followed_user=user_to_unfollow
        )
        if follow_relation.exists():
            follow_relation.delete()
            messages.success(request, f"Vous ne suivez plus {user_to_unfollow.username}.")
        else:
            messages.error(request, "Vous ne suiviez pas cet utilisateur.")
    return redirect('subscriptions')
