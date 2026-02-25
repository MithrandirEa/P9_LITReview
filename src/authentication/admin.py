from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuration de l'administration pour le modèle User personnalisé.
    Hérite de la configuration par défaut de UserAdmin mais personnalise les champs affichés.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
