from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<str:username>/', views.profile, name='profile'),  
    path('home_profile/<str:username>/', views.home_profile, name='home_profile'),
    path('settings/<str:username>/', views.settings, name='settings'),
]