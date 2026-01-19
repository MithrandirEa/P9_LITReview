# LITReview

Application web Django permettant de demander et publier des critiques de livres.

## Description

LITReview est une application permettant aux utilisateurs de :
- Créer des tickets pour demander des critiques sur des livres
- Publier des critiques en réponse aux tickets
- Créer des critiques directement (ticket + critique en une fois)
- Suivre d'autres utilisateurs pour voir leurs publications
- Bloquer des utilisateurs indésirables

## Technologies utilisées

- Python 3.x
- Django 6.0.1
- SQLite
- Bootstrap 5 (via django-crispy-forms)
- Pillow (gestion des images)

## Prérequis

- Python 3.8 ou supérieur
- pip

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-depot>
cd LITReview
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### 3. Activer l'environnement virtuel

**Windows :**
```bash
venv\Scripts\activate
```

**macOS/Linux :**
```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Migrations de base de données

Se placer dans le dossier `src` :
```bash
cd src
```

Appliquer les migrations :
```bash
python manage.py migrate
```

### 2. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 3. Collecte des fichiers statiques (optionnel pour développement)

```bash
python manage.py collectstatic
```

## Utilisation

### Démarrer le serveur de développement

Depuis le dossier `src` :
```bash
python manage.py runserver
```

Le site sera accessible à l'adresse : `http://127.0.0.1:8000/`

### Accéder à l'interface d'administration

L'interface d'administration Django est disponible à : `http://127.0.0.1:8000/admin/`

## Structure du projet

```
LITReview/
├── src/
│   ├── manage.py              # Point d'entrée Django
│   ├── db.sqlite3             # Base de données SQLite
│   ├── LITReview/             # Configuration du projet
│   │   ├── settings.py        # Paramètres Django
│   │   ├── urls.py            # Routes principales
│   │   └── wsgi.py            # Configuration WSGI
│   ├── authentication/         # Application d'authentification
│   │   ├── models.py          # Modèle User personnalisé
│   │   ├── views.py           # Vues (login, signup)
│   │   ├── forms.py           # Formulaires d'authentification
│   │   └── templates/         # Templates HTML
│   ├── flux/                  # Application principale
│   │   ├── models.py          # Modèles (Ticket, Review, UserFollows, UserBlocks)
│   │   ├── views.py           # Vues du flux et gestion des posts
│   │   ├── forms.py           # Formulaires de création/édition
│   │   └── templates/         # Templates HTML
│   ├── media/                 # Fichiers uploadés par les utilisateurs
│   └── static/                # Fichiers statiques (CSS, images)
├── requirements.txt           # Dépendances Python
└── README.md                  # Documentation
```

## Fonctionnalités

### Authentification
- Inscription de nouveaux utilisateurs
- Connexion/déconnexion
- Groupes d'utilisateurs (créés automatiquement)

### Gestion des tickets
- Création de demandes de critiques
- Modification et suppression de ses propres tickets
- Ajout d'images optionnelles

### Gestion des critiques
- Réponse aux tickets d'autres utilisateurs
- Création de critiques avec tickets intégrés
- Modification et suppression de ses propres critiques
- Système de notation par étoiles (0-5)

### Flux social
- Affichage du flux personnalisé (posts des utilisateurs suivis + posts personnels)
- Affichage de tous les posts personnels
- Gestion des abonnements (suivre/ne plus suivre)
- Blocage d'utilisateurs

## Modèles de données

### User
Modèle personnalisé héritant de AbstractUser de Django.

### Ticket
- title : titre du livre/demande
- description : description de la demande
- user : créateur du ticket
- image : image optionnelle
- time_created : date de création

### Review
- ticket : ticket associé
- rating : note de 0 à 5
- headline : titre de la critique
- body : contenu de la critique
- user : auteur de la critique
- time_created : date de création

### UserFollows
- user : utilisateur qui suit
- followed_user : utilisateur suivi

### UserBlocks
- user : utilisateur qui bloque
- blocked_user : utilisateur bloqué

## Commandes utiles

### Créer une nouvelle migration
```bash
python manage.py makemigrations
```

### Appliquer les migrations
```bash
python manage.py migrate
```

### Lancer les tests
```bash
python manage.py test
```

### Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### Accéder au shell Django
```bash
python manage.py shell
```

## Développement

### Fichier settings.py
Le fichier `settings.py` contient la configuration du projet. Les paramètres importants :
- `DEBUG = True` : mode debug (à désactiver en production)
- `SECRET_KEY` : clé secrète (à changer en production)
- `ALLOWED_HOSTS` : liste des hôtes autorisés
- `INSTALLED_APPS` : applications installées
- `AUTH_USER_MODEL` : modèle User personnalisé

### Ordre des migrations
Les migrations doivent être appliquées dans l'ordre pour éviter les problèmes de dépendances entre les modèles.

## Sécurité

**Important pour la production :**
- Modifier la `SECRET_KEY` dans settings.py
- Définir `DEBUG = False`
- Configurer `ALLOWED_HOSTS` avec les domaines autorisés
- Utiliser une base de données plus robuste (PostgreSQL, MySQL)
- Configurer HTTPS
- Gérer les fichiers statiques avec un serveur web (nginx, Apache)

## Licence

Projet réalisé dans le cadre d'une formation OpenClassrooms.
