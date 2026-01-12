from django.contrib.auth.models import AbstractUser
from django.db import models

"""
Attention : AVANT TOUTE MIGRATION, vérifier que les 
rôles d'utilisateur et superutilisateur sont définis.
"""


class User(AbstractUser):

    CREATOR = 'CREATOR'
    SUBSCRIBER = 'SUBSCRIBER'

    ROLE_CHOICES = (
        (CREATOR, 'Créateur'),
        (SUBSCRIBER, 'Abonné'),
    )

    profile_picture = models.ImageField()
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,      
    )
