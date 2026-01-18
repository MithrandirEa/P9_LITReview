from django.contrib import admin
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView, 
                                       PasswordChangeDoneView)
from django.urls import path

import authentication.views
import flux.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(
        template_name='authentication/login.html',
        redirect_authenticated_user=True),
        name='login'),
    path('signup/', authentication.views.signup_page, name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('flux/', flux.views.flux, name='flux'),
    path('posts/', flux.views.posts, name='posts'),
    path('subscriptions/', flux.views.subscriptions, name='subscriptions'),

]
