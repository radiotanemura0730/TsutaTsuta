from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('signup_auth/<int:user_id>', views.SignUpAuthView.as_view(), name='signup_auth'),
    path("", views.index, name="index"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("home_profile/<str:username>/", views.home_profile, name="home_profile"),
    path("settings/<str:username>/", views.settings, name="settings"),
    path("edit_profile/<str:username>", views.edit_profile, name="edit_profile"),
    path("home/", views.home_view, name="home"),
    path(
        "product_description/<int:product_id>/",
        views.product_description,
        name="product_description",
    ),
]
