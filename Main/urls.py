from django.urls import path

from . import views

urlpatterns = [
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('signup_auth/<int:pk>', views.SignUpAuthView.as_view(), name='signup_auth'),
    path('signup_done/<int:pk>', views.SignUpDoneView.as_view(), name='signup_done'),
    path("", views.index, name="index"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("home_profile/<str:username>/", views.home_profile, name="home_profile"),
    path("user_settings/<str:username>/", views.user_settings, name="user_settings"),
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
    path("liked_products/<str:username>/", views.liked_products, name="liked_products"),
    path(
        "bought_products/<str:username>", views.bought_products, name="bought_products"
    ),
    path("payment_information/", views.payment_information, name="payment_information"),
    path("create_card/", views.create_card, name="create-card-information"),
    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),
    path("rules/", views.rules, name="rules"),
]
