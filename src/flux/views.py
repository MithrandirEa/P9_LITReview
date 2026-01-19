from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from flux.forms import TicketForm, ReviewForm

"""Le décorateur login_required garantit que seuls les utilisateurs
 authentifiés peuvent accéder à cette vue."""


@login_required
def flux(request):
    return render(request, 'flux/flux.html')

@login_required
def posts(request):
    return render(request, 'flux/posts.html')

@login_required
def subscriptions(request):
    return render(request, 'flux/subscriptions.html')

@login_required
def create_review(request):
    return render(request, 'flux/create_review.html')

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
