from django.conf import settings
from django.contrib.auth import logout, login
from django.shortcuts import redirect, render

from . import forms


def logout_user(request):
    """
    Vue permettant de déconnecter l'utilisateur.

    Args:
        request (HttpRequest): La requête HTTP.

    Returns:
        HttpResponseRedirect: Redirige vers la page de connexion après la déconnexion.
    """
    logout(request)
    return redirect('login')


def signup_page(request):
    """
    Vue gérant l'inscription des nouveaux utilisateurs.

    Args:
        request (HttpRequest): La requête HTTP qui peut contenir les données du formulaire.

    Returns:
        HttpResponse: Rend le template d'inscription avec le formulaire ou redirige après une inscription réussie.
    """
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authentication/signup.html', {'form': form})
