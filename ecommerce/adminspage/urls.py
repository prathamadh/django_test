from django.urls import path
from .views import *
from . import views
urlpatterns=[
    path('dashboard/',dashboard),
    path('orders/',order),
    path('users/', views.show_logged_in_users, name='show_logged_in_users'),


]