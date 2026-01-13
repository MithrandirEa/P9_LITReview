from django.conf import settings
from django.contrib.auth import logout, login
from django.shortcuts import redirect, render

from . import forms


def logout_user(request):
    logout(request)
    return redirect('login')


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authentication/signup.html', {'form': form})


def change_password(request):
    form = forms.ChangePasswordForm(user=request.user)
    if request.method == 'POST':
        form = forms.ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_change_done')
    return render(request, 'authentication/password_change_form.html', {'form': form})