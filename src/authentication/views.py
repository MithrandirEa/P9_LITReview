from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from . import forms


def login_page(request):
    form = forms.LoginForm()
    message = ''
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                message = 'Connexion réussie'
            else:
                message = 'Identifiants invalides'
    return render(
        request, 'authentication/login.html',
        {'form': form, 'message': message})


def logout_page(request):
    pass
    return redirect('login')
