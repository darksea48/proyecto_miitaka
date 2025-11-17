from django import template
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]