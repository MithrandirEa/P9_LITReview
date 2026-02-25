from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model

from flux.forms import TicketForm, ReviewForm, ReviewReplyForm
from flux.models import Ticket, Review, UserFollows, UserBlocks

User = get_user_model()

# ------------ Vues pour les onglets de l'app -------------


@login_required
def flux(request):
    """
    Vue principale du flux d'activité.
    Affiche les tickets et les critiques des utilisateurs suivis, ainsi que ses propres posts.
    Les éléments sont triés par date de création décroissante.
    Exclut les tickets qui ont déjà reçu une critique de la part d'un utilisateur suivi.

    Args:
        request (HttpRequest): La requête HTTP.

    Returns:
        HttpResponse: Rend le template 'flux.html' avec le contexte des 'posts'.
    """
    # Récupérer les IDs des utilisateurs suivis
    followed_users = User.objects.filter(
        id__in=UserFollows.objects.filter(user=request.user).values_list(
            'followed_user', flat=True
        )
    )
    # Récupérer les critiques de l'utilisateur, des utilisateurssuivis,
    # et les critiques sur les tickets créés par les suivis
    reviews = (
        Review.objects.filter(user__in=followed_users) |
        Review.objects.filter(user=request.user) |
        Review.objects.filter(ticket__user__in=followed_users)
    ).distinct()
    # Récupérer les IDs des tickets qui ont déjà une critique
    reviewed_ticket_ids = reviews.values_list('ticket_id', flat=True)

    # Tickets de l'utilisateur et des suivis (sans ceux ayant une critique)
    tickets = (
        Ticket.objects.filter(user__in=followed_users) |
        Ticket.objects.filter(user=request.user)
    ).exclude(id__in=reviewed_ticket_ids)

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
    """
    Vue affichant les propres posts de l'utilisateur (tickets et critiques).
    Permet de voir l'historique de ses contributions.
    Exclut les tickets qui ont déjà reçu une critique de l'utilisateur lui-même (si applicable pour éviter doublons visuels,
    bien que la logique ici semble exclure les tickets que l'User a déjà critiqué, ce qui est une règle métier).

    Args:
        request (HttpRequest): La requête HTTP.

    Returns:
        HttpResponse: Rend le template 'posts.html' avec la liste des posts.
    """
    reviews = Review.objects.filter(user=request.user)
    # Récupérer les IDs des tickets qui ont déjà une critique
    reviewed_ticket_ids = reviews.values_list('ticket_id', flat=True)

    # Exclure ces tickets de la liste
    tickets = Ticket.objects.filter(user=request.user).exclude(
        id__in=reviewed_ticket_ids
    )

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
    """
    Vue permettant de gérer les abonnements :
    - S'abonner à un nouvel utilisateur.
    - Voir la liste des utilisateurs que l'on suit.
    - Voir la liste des utilisateurs bloqués.
    - Voir la liste des abonnés (followers).

    Gère les erreurs (utilisateur inexistant, auto-follow, déjà suivi).

    Args:
        request (HttpRequest): La requête HTTP, potentiellement POST pour s'abonner.

    Returns:
        HttpResponse: Rend le template 'subscriptions.html' avec les contextes :
            'users_followed': Liste des utilisateurs suivis.
            'followers': Liste des utilisateurs qui nous suivent.
            'blocked_users': Liste des utilisateurs bloqués.
    """
    # Gestion d'un nouvel abonnement
    if request.method == 'POST' and 'username' in request.POST:
        username = request.POST.get('username')
        try:
            user_to_follow = User.objects.get(username=username)
            if user_to_follow == request.user:
                messages.error(
                    request, "Vous ne pouvez pas vous suivre vous-même."
                )
            elif UserFollows.objects.filter(
                user=request.user, followed_user=user_to_follow
            ).exists():
                messages.warning(request, f"Vous suivez déjà {username}.")
            else:
                UserFollows.objects.create(
                    user=request.user, followed_user=user_to_follow
                )
                messages.success(
                    request, f"Vous suivez maintenant {username}."
                )
        except User.DoesNotExist:
            messages.error(request, f"L'utilisateur {username} n'existe pas.")
        return redirect('subscriptions')

    # Récupération des utilisateurs suivis
    users_followed = User.objects.filter(
        id__in=UserFollows.objects.filter(user=request.user).values_list(
            'followed_user', flat=True
        )
    )

    # Récupération des abonnés (followers)
    followers = User.objects.filter(
        id__in=UserFollows.objects.filter(
            followed_user=request.user
        ).values_list('user', flat=True)
    )

    # Récupération des utilisateurs bloqués
    blocked_users = User.objects.filter(
        id__in=UserBlocks.objects.filter(user=request.user).values_list(
            'blocked_user', flat=True
        )
    )

    context = {
        'users_followed': users_followed,
        'followers': followers,
        'blocked_users': blocked_users,
    }
    return render(request, 'flux/subscriptions.html', context)


# ------------ Vues pour les actions sur les tickets et critiques -------------


@login_required
def create_review(request):
    """
    Vue permettant de créer une critique (Review) en même temps qu'un ticket.
    Utile quand l'utilisateur veut faire une critique d'un livre/article qu'il n'a pas encore demandé.
    Gère deux formulaires simultanément : ReviewForm et TicketForm.

    Args:
        request (HttpRequest): La requête HTTP, potentiellement POST.

    Returns:
        HttpResponse: Rend le template 'create_review.html' ou redirige vers le flux.
    """
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
    """
    Vue permettant de répondre à un ticket existant en créant une critique.
    Récupère le ticket associé par son ID.
    Le titre de la critique est généré automatiquement.

    Args:
        request (HttpRequest): La requête HTTP.
        ticket_id (int): L'ID du ticket auquel répondre.

    Returns:
        HttpResponse: Rend le template 'create_review_reply.html' ou redirige vers le flux.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        review_form = ReviewReplyForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            # Générer automatiquement le headline basé sur le titre
            review.headline = f"Critique de {ticket.title}"
            review.save()
            messages.success(
                request, "Votre critique a été publiée avec succès."
            )
            return redirect('flux')
    else:
        review_form = ReviewReplyForm()
    return render(request, 'flux/create_review_reply.html', {
        'review_form': review_form,
        'ticket': ticket
    })


@login_required
def create_ticket(request):
    """
    Vue permettant de créer un nouveau ticket (demande de critique).
    Le ticket peut contenir une image uploadée.

    Args:
        request (HttpRequest): La requête HTTP.

    Returns:
        HttpResponse: Rend le template 'create_ticket.html' ou redirige vers le flux.
    """
    form = TicketForm()
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('flux')
    return render(request, 'flux/create_ticket.html', {'form': form})


@login_required
def edit_ticket(request, ticket_id):
    """
    Vue permettant de modifier un ticket existant.
    Vérifie que l'utilisateur est le propriétaire du ticket avant de permettre l'édition.

    Args:
        request (HttpRequest): La requête HTTP.
        ticket_id (int): L'ID du ticket à modifier.

    Returns:
        HttpResponse: Rend le template 'edit_ticket.html' ou redirige vers 'posts'.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    # Vérifier que l'utilisateur est bien le propriétaire
    if ticket.user != request.user:
        messages.error(request, "Vous ne pouvez pas modifier ce ticket.")
        return redirect('posts')
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Votre ticket a été modifié avec succès."
            )
    """
    Vue permettant de modifier une critique existante.
    Vérifie que l'utilisateur est le propriétaire de la critique avant de permettre l'édition.

    Args:
        request (HttpRequest): La requête HTTP.
        review_id (int): L'ID de la critique à modifier.

    Returns:
        HttpResponse: Rend le template 'edit_review.html' ou redirige vers 'posts'.
    """
            return redirect('posts')
    else:
        form = TicketForm(instance=ticket)

    return render(
        request, 'flux/edit_ticket.html', {'form': form, 'ticket': ticket}
    )


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
            messages.success(
                request, "Votre critique a été modifiée avec succès."
            )
            return redirect('posts')
    else:
        form = ReviewForm(instance=review)

    return render(
        request, 'flux/edit_review.html', {'form': form, 'review': review}
    )


@login_required
def delete_ticket(request, ticket_id):
    """
    Vue permettant de supprimer un ticket.
    Vérifie que l'utilisateur est le propriétaire du ticket.
    La suppression doit être confirmée par une requête POST.

    Args:
        request (HttpRequest): La requête HTTP (POST nécessaire pour supprimer).
        ticket_id (int): L'ID du ticket à supprimer.

    Returns:
        HttpResponseRedirect: Redirige vers 'posts'.
    """
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
def delete_review(request, review_id):
    """
    Vue permettant de supprimer une critique.
    Vérifie que l'utilisateur est le propriétaire de la critique.
    La suppression doit être confirmée par une requête POST.

    Args:
        request (HttpRequest): La requête HTTP (POST nécessaire pour supprimer).
        review_id (int): L'ID de la critique à supprimer.

    Returns:
        HttpResponseRedirect: Redirige vers 'posts'.
    """
    review = get_object_or_404(Review, id=review_id)
    # Vérifier que l'utilisateur est bien le propriétaire
    if review.user != request.user:
        messages.error(request, "Vous ne pouvez pas supprimer cette critique.")
        return redirect('posts')
    if request.method == 'POST':
        review.delete()
        messages.success(
            request, "Votre critique a été supprimée avec succès."
        )

    return redirect('posts')


# ------------ Vues pour les actions sur le suivi et le blocage utilisateur -------------


@login_required
def unfollow_user(request, user_id):
    """
    Vue permettant de ne plus suivre un utilisateur.
    Vérifie l'existence de la relation avant de supprimer.

    Args:
        request (HttpRequest): La requête HTTP (POST).
        user_id (int): L'ID de l'utilisateur à ne plus suivre.

    Returns:
        HttpResponseRedirect: Redirige vers 'subscriptions'.
    """
    if request.method == 'POST':
        user_to_unfollow = get_object_or_404(User, id=user_id)
        follow_relation = UserFollows.objects.filter(
            user=request.user,
            followed_user=user_to_unfollow
        )
        if follow_relation.exists():
            follow_relation.delete()
            messages.success(
                request, f"Vous ne suivez plus {user_to_unfollow.username}."
            )
        else:
            messages.error(request, "Vous ne suiviez pas cet utilisateur.")
    return redirect('subscriptions')


@login_required
def block_user(request, user_id):
    """
    Vue permettant de bloquer un utilisateur.
    Supprime également tout abonnement existant (dans les deux sens) avec cet utilisateur.
    Gère les erreurs (auto-block, déjà bloqué).

    Args:
        request (HttpRequest): La requête HTTP (POST).
        user_id (int): L'ID de l'utilisateur à bloquer.

    Returns:
        HttpResponseRedirect: Redirige vers 'subscriptions'.
    """
    if request.method == 'POST':
        user_to_block = get_object_or_404(User, id=user_id)

        if user_to_block == request.user:
            messages.error(
                request, "Vous ne pouvez pas vous bloquer vous-même."
            )
        elif UserBlocks.objects.filter(
            user=request.user, blocked_user=user_to_block
        ).exists():
            messages.warning(
                request, f"Vous avez déjà bloqué {user_to_block.username}."
            )
        else:
            # Créer le blocage
            UserBlocks.objects.create(
                user=request.user, blocked_user=user_to_block
            )

            # Supprimer les relations d'abonnement mutuelles
            UserFollows.objects.filter(
                user=request.user, followed_user=user_to_block
            ).delete()
    """
    Vue permettant de débloquer un utilisateur.
    Vérifie l'existence du blocage avant de supprimer.

    Args:
        request (HttpRequest): La requête HTTP (POST).
        user_id (int): L'ID de l'utilisateur à débloquer.

    Returns:
        HttpResponseRedirect: Redirige vers 'subscriptions'.
    """
            UserFollows.objects.filter(
                user=user_to_block, followed_user=request.user
            ).delete()

            messages.success(
                request, f"Vous avez bloqué {user_to_block.username}."
            )
    return redirect('subscriptions')


@login_required
def unblock_user(request, user_id):
    if request.method == 'POST':
        user_to_unblock = get_object_or_404(User, id=user_id)
        block_relation = UserBlocks.objects.filter(
            user=request.user,
            blocked_user=user_to_unblock
        )
        if block_relation.exists():
            block_relation.delete()
            messages.success(
                request,
                f"Vous avez débloqué {user_to_unblock.username}."
            )
        else:
            messages.error(
                request, "Vous n'aviez pas bloqué cet utilisateur."
            )
    return redirect('subscriptions')
