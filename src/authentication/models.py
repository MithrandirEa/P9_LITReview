from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Modèle d'utilisateur personnalisé étendant AbstractUser.
    Permet d'ajouter des champs ou des relations spécifiques à l'utilisateur si nécessaire.
    """
    pass
