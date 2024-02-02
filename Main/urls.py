from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('signup_auth/<int:user_id>', views.SignUpAuthView.as_view(), name='signup_auth'),
]