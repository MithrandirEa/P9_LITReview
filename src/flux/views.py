from django.contrib.auth.decorators import login_required
from django.shortcuts import render

"""Le décorateur login_required garantit que seuls les utilisateurs
 authentifiés peuvent accéder à cette vue."""


@login_required
def home(request):
    return render(request, 'flux/home.html')
