from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
    return render(request, 'flux/create_revue.html')

@login_required
def create_ticket(request, post_id):
    return render(request, 'flux/create_ticket.html', {'post_id': post_id})
