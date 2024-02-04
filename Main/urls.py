from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("home_profile/<str:username>/", views.home_profile, name="home_profile"),
    path("settings/<str:username>/", views.user_settings, name="settings"),
    path("edit_profile/<str:username>", views.edit_profile, name="edit_profile"),
    path("home/", views.home_view, name="home"),
    path(
        "product_description/<int:product_id>/",
        views.product_description,
        name="product_description",
    ),
    path("edit_profile/<str:username>/", views.edit_profile, name="edit_profile"),
    path("delete_profile/<str:username>/", views.delete_profile, name="delete_profile"),
    path("delete_confirm/", views.delete_confirm, name="delete_confirm"),
    path("payment_information/", views.payment_information, name="payment_information"),
    path("create_card/", views.create_card, name="create-card-information"), # クレジットカード登録
]
