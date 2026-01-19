from django.contrib import admin
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView, 
                                       PasswordChangeDoneView)
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

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
    path('create-review/', flux.views.create_review, name='create_review'),
    path('ask-ticket/', flux.views.ask_ticket, name='ask_ticket'),
    
    # Path pour le système d'abonnement
    path('unfollow/<int:user_id>/', flux.views.unfollow_user, name='unfollow'),
]



if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
