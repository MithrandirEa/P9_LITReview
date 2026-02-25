from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Ticket(models.Model):
    """
    Modèle représentant un ticket (demande de critique).
    Lié à un utilisateur, avec un titre, une description optionnelle et une image optionnelle.
    """
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    """
    Modèle représentant une critique sur un ticket.
    Liée à un ticket, un utilisateur, contient une note (0-5), un titre et un corps.
    """
    ticket = models.ForeignKey(to='flux.Ticket', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

"""
    Modèle de relation pour suivre des utilisateurs.
    Définit une relation 'following' (qui suit) et 'followed_by' (qui est suivi).
    Garantit l'unicité des paires (user, followed_user).
    """
    
class UserFollows(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followed_by'
    )

    """
    Modèle pour gérer le blocage d'utilisateurs.
    Définit qui bloque qui.
    L'utilisateur qui bloque est 'user', l'utilisateur bloqué est 'blocked_user'.
    """
    class Meta:
        unique_together = ('user', 'followed_user', )


class UserBlocks(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocking'
    )
    blocked_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_by'
    )
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blocked_user', )
