from django.shortcuts import render
from django.conf import settings
from django.views import View
from django.views.generic import TemplateView
from .models import Product
from django.shortcuts import redirect
import stripe
# Create your views here.

# WEBHOOKのシークレットキー
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

def credit_card(request):
    user = request.user
    # セッションを開始するため、STRIPEのシークレットキーをセットする
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Customerオブジェクトを作成（引数は任意）
    stripe_customer = stripe.Customer.create(
        name=user.username
    )
    # SetupIntentオブジェクト生成
    setup_intent = stripe.SetupIntent.create(
        customer=stripe_customer.id,# 生成したCustomerのIDを指定
        payment_method_types=["card"],# 支払い方法→今回はクレジットカード（"card"）
        )
        # 作成したSetupIntentからclient_secretを取得する→テンプレートへ渡す
    context = {
        "client_secret": setup_intent.client_secret,
    }
    template_name = 'create_card_information.html'
    return render(request, template_name, context)

