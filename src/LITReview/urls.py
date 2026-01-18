from django.contrib import admin
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView, 
                                       PasswordChangeDoneView)
from django.urls import path

import authentication.views
import flux.views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Path de login, logout, signup
    path('', LoginView.as_view(
        template_name='authentication/login.html',
        redirect_authenticated_user=True),
        name='login'),
    path('signup/', authentication.views.signup_page, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Path de l'affichage des pages flux, posts, subscriptions
    path('flux/', flux.views.flux, name='flux'),
    path('posts/', flux.views.posts, name='posts'),
    path('subscriptions/', flux.views.subscriptions, name='subscriptions'),

    # Path de création de critiques et de tickets
    path('create-revue/', flux.views.create_review, name='create_review'),
    path('create-ticket/', flux.views.create_ticket, name='create_ticket'),



]
