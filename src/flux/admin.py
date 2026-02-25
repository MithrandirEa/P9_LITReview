from django.contrib import admin
from .models import Ticket, Review, UserFollows

# Register your models here.

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration pour les tickets.
    Affiche le titre, l'utilisateur et la date de création.
    Permet la recherche par titre et utilisateur.
    Permet le filtrage par date.
    """
    list_display = ('title', 'user', 'time_created')
    search_fields = ('title', 'user__username')
    list_filter = ('time_created',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration pour les critiques (Reviews).
    Affiche le titre, le ticket associé, l'utilisateur, la note et la date.
    Permet la recherche par titre, titre du ticket et utilisateur.
    Permet le filtrage par note et date.
    """
    list_display = ('headline', 'ticket', 'user', 'rating', 'time_created')
    search_fields = ('headline', 'ticket__title', 'user__username')
    list_filter = ('rating', 'time_created')

@admin.register(UserFollows)
class UserFollowsAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration pour les abonnements (UserFollows).
    Affiche l'utilisateur suiveur et l'utilisateur suivi.
    Permet la recherche sur les deux noms d'utilisateur.
    """
    list_display = ('user', 'followed_user')
    search_fields = ('user__username', 'followed_user__username')

