from django.contrib import admin
from django.urls import path
from rest_framework import routers

from users.views import LogInView, LogOutView, ProfileView, ChangePasswordView

urlpatterns = [
    path('login/', LogInView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('change_password/', ChangePasswordView.as_view()),
    path('profile/', ProfileView.as_view()),
]
