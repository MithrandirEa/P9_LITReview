from itertools import chain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from flux.forms import TicketForm, ReviewForm, ReviewReplyForm
from flux.models import Ticket, Review, UserFollows

User = get_user_model()

"""Le décorateur login_required garantit que seuls les utilisateurs
 authentifiés peuvent accéder à cette vue."""


@login_required
def flux(request):
    # Récupérer les IDs des utilisateurs suivis
    followed_users = User.objects.filter(
        id__in=UserFollows.objects.filter(user=request.user).values_list('followed_user', flat=True)
    )
    
    # Récupérer les critiques de l'utilisateur et des utilisateurs suivis
    reviews = Review.objects.filter(user__in=followed_users) | Review.objects.filter(user=request.user)
    
    # Récupérer les IDs des tickets qui ont déjà une critique
    reviewed_ticket_ids = reviews.values_list('ticket_id', flat=True)
    
    # Récupérer les tickets de l'utilisateur et des utilisateurs suivis, en excluant ceux qui ont déjà une critique
    tickets = (Ticket.objects.filter(user__in=followed_users) | Ticket.objects.filter(user=request.user)).exclude(id__in=reviewed_ticket_ids)

    # Créer une liste unifiée
    posts = []
    
    for ticket in tickets:
        ticket.content_type = 'TICKET'
        ticket.content = ticket.description
        posts.append(ticket)
    
    for review in reviews:
        review.content_type = 'REVIEW'
        review.title = review.headline
        review.content = review.body
        posts.append(review)
    
    # Tri par date de création
    posts = sorted(posts, key=lambda post: post.time_created, reverse=True)

    return render(request, 'flux/flux.html', context={'posts': posts})

@login_required
def posts(request):
    reviews = Review.objects.filter(user=request.user)
    
    # Récupérer les IDs des tickets qui ont déjà une critique de l'utilisateur
    reviewed_ticket_ids = reviews.values_list('ticket_id', flat=True)
    
    # Exclure ces tickets de la liste
    tickets = Ticket.objects.filter(user=request.user).exclude(id__in=reviewed_ticket_ids)

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
def create_review_reply(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        review_form = ReviewReplyForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            # Générer automatiquement le headline basé sur le titre du ticket
            review.headline = f"Critique de {ticket.title}"
            review.save()
            messages.success(request, "Votre critique a été publiée avec succès.")
            return redirect('flux')
    else:
        review_form = ReviewReplyForm()
    
    return render(request, 'flux/create_review_reply.html', {
        'review_form': review_form,
        'ticket': ticket
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

@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire
    if ticket.user != request.user:
        messages.error(request, "Vous ne pouvez pas modifier ce ticket.")
        return redirect('posts')
    
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre ticket a été modifié avec succès.")
            return redirect('posts')
    else:
        form = TicketForm(instance=ticket)
    
    return render(request, 'flux/edit_ticket.html', {'form': form, 'ticket': ticket})

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire
    if ticket.user != request.user:
        messages.error(request, "Vous ne pouvez pas supprimer ce ticket.")
        return redirect('posts')
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Votre ticket a été supprimé avec succès.")
    
    return redirect('posts')

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire
    if review.user != request.user:
        messages.error(request, "Vous ne pouvez pas modifier cette critique.")
        return redirect('posts')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre critique a été modifiée avec succès.")
            return redirect('posts')
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'flux/edit_review.html', {'form': form, 'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire
    if review.user != request.user:
        messages.error(request, "Vous ne pouvez pas supprimer cette critique.")
        return redirect('posts')
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Votre critique a été supprimée avec succès.")
    
    return redirect('posts')
