from django.urls import path
from . import views

urlpatterns = [
    path('credit_card_information/', views.credit_card, name="create-card-information"), # 決済機能  
]