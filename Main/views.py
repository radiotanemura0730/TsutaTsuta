from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Q, Subquery, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import UserProfileForm, SignUpForm, AvailableProductsForm, OnTransactionProductsForm, UserAddressForm
from .models import Class, CustomUser, Product, Review, Transaction, Like
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
import random

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'Main/signup.html'

    def form_valid(self, form):
        super().form_valid(form)
        random_number = random.randint(1000,9999)
        random_number_str = str(random_number)
        to_email = form.cleaned_data['email']
        subject = "題名"
        message = "認証番号の" + random_number_str + "を入力してください"
        from_email = "system@example.com"
        recipient_list = [to_email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("send_email")
        user_record = CustomUser.objects.get(email=to_email)
        self.user_id = int(user_record.id)
        return redirect("signup_auth", user_id=self.object.id)
    
    def get_success_url(self) -> str:
        return reverse_lazy('signup_auth', kwargs={'user_id' : self.object.id})
    
    
class SignUpAuthView(TemplateView):
    template_name = 'Main/signup_auth.html'

def index(request):
    return render(request, "index.html")

@login_required
def profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    is_own_profile = user == request.user

    user_products = Product.objects.filter(seller=user)

    reviews = Review.objects.filter(user=user)

    if reviews.exists():
        average_rating = sum([review.evaluate for review in reviews]) / len(reviews)
        average_rating = round(average_rating, 0)
        average_rating = int(average_rating)
        average_rate = list(range(average_rating))
        subtract_rating = list(range(5 - average_rating))
    else:
        average_rate = None
        subtract_rating = list(range(5))

    review_number = len(reviews)

    latest_user_products = user_products.order_by("-created_at")[:6]
    relatively_latest_user_products = user_products.order_by("-created_at")[6:12]

    context = {
        "user": user,
        "is_own_profile": is_own_profile,
        "latest_user_products": latest_user_products,
        "relatively_latest_user_products": relatively_latest_user_products,
        "average_rating": average_rate,
        "subtract_rating": subtract_rating,
        "review_number": review_number,
    }

    return render(request, "profile.html", context)


@login_required
def home_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    reviews = Review.objects.filter(user=user)

    if reviews.exists():
        average_rating = sum([review.evaluate for review in reviews]) / len(reviews)
        average_rating = round(average_rating, 0)
        average_rating = int(average_rating)
        average_rate = list(range(average_rating))
        subtract_rating = list(range(5 - average_rating))
    else:
        average_rate = None
        subtract_rating = list(range(5))

    review_number = len(reviews)

    total_profit = Product.objects.filter(seller=user).aggregate(Sum("price"))[
        "price__sum"
    ] or Decimal("0.0")

    # ポイントに関する機能は後で実装

    context = {
        "user": user,
        "average_rating": average_rate,
        "subtract_rating": subtract_rating,
        "review_number": review_number,
        "total_profit": total_profit,
    }

    return render(request, "home_profile.html", context)


@login_required
def user_settings(request, username):
    user = get_object_or_404(CustomUser, username=username)

    context = {
        "user": user,
    }

    return render(request, "user_settings.html", context)


@login_required
def edit_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    if request.method == "POST":
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)

        if user_form.is_valid():
            user_form.save()
            return redirect(reverse("home_profile", args=[username]))

    else:
        user_form = UserProfileForm(instance=user)

    return render(request, "edit_profile.html", {"user_form": user_form})


@login_required
def delete_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    is_own_profile = user == request.user

    user_products = Product.objects.filter(seller=user)

    reviews = Review.objects.filter(user=user)

    if reviews.exists():
        average_rating = sum([review.evaluate for review in reviews]) / len(reviews)
        average_rating = round(average_rating, 0)
        average_rating = int(average_rating)
        average_rate = list(range(average_rating))
        subtract_rating = list(range(5 - average_rating))
    else:
        average_rate = None
        subtract_rating = list(range(5))

    review_number = len(reviews)

    latest_user_products = user_products.order_by("-created_at")[:6]
    relatively_latest_user_products = user_products.order_by("-created_at")[6:12]

    if request.method == "POST":
        user.delete()
        return redirect("index")

    context = {
        "user": user,
        "is_own_profile": is_own_profile,
        "latest_user_products": latest_user_products,
        "relatively_latest_user_products": relatively_latest_user_products,
        "average_rating": average_rate,
        "subtract_rating": subtract_rating,
        "review_number": review_number,
    }

    return render(request, "delete_profile.html", context)

def edit_address(request, username):
    user = get_object_or_404(CustomUser, username=username)

    if request.method == "POST":
        user_form = UserAddressForm(request.POST, request.FILES, instance=user)

        if user_form.is_valid():
            user_form.save()
            return redirect(reverse("home_profile", args=[username]))

    else:
        user_form = UserAddressForm(instance=user)
    return render(request, "edit_address.html", {"user_form":user_form})


@login_required
def home_view(request):
    user = request.user
    faculity = Product.FACULTY_CHOICES
    department = Product.DEPARTMENT_CHOICES
    transaction_exists = Transaction.objects.filter(
        product_id=OuterRef("pk"), buyer__isnull=False
    ).values("product_id")[:1]
    products_list = Product.objects.exclude(
        Q(seller=user) | Q(pk__in=Subquery(transaction_exists))
    )
    classrooms = Class.objects.all()
    studies_list = []
    for classroom in classrooms:
        for gakubu in faculity:
            for gakka in department:
                for product in products_list:
                    if product.classroom_category == classroom:
                        if product.gakubu_category == gakubu[1]:
                            if product.gakka_category == gakka[1]:
                                studies_list.append([classroom, gakubu[1], gakka[1]])
                                break
    context = {
        "user": user,
        "products_list": products_list,
        "studies_list": studies_list,
    }
    print(studies_list)
    return render(request, "home.html", context)


@login_required
def product_description(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)
    review = Review.objects.get(user=product.seller)
    context = {
        "user": user,
        "product": product,
        "review": review,
    }
    return render(request, "product_description.html", context)


def delete_confirm(request):
    return render(request, "delete_confirm.html")


@login_required
def liked_products(request, username):
    user = get_object_or_404(CustomUser, username=username)

    if request.method == "POST":
        form = AvailableProductsForm(request.POST)
        if form.is_valid():
            available_filter = {"user": user}

            # チェックボックスにチェックが入っている場合はis_availableの条件を追加
            if form.cleaned_data["show_available"]:
                available_filter["product__is_available"] = True

            user_likes = Like.objects.filter(**available_filter)

    else:
        form = AvailableProductsForm()
        user_likes = Like.objects.filter(user=user)

    liked_products = [like.product for like in user_likes]

    context = {"user": user, "liked_products": liked_products, "form": form}

    return render(request, "liked_products.html", context)


@login_required
def bought_products(request, username):
    user = get_object_or_404(CustomUser, username=username)

    if request.method == "POST":
        form = OnTransactionProductsForm(request.POST)
        if form.is_valid():
            available_filter = {"buyer": user}

            # チェックボックスにチェックが入っている場合はis_availableの条件を追加
            if form.cleaned_data["show_available"]:
                available_filter["product__is_available"] = True

            bought_products = Transaction.objects.filter(**available_filter)

    else:
        form = OnTransactionProductsForm(request.POST)
        bought_products = Transaction.objects.filter(buyer=user)

    bought_products = [transaction.product for transaction in bought_products]

    context = {
        "user": user,
        "bought_products": bought_products,
        "form": form,
    }

    return render(request, "bought_products.html", context)


def payment_information(request, username):
    user = get_object_or_404(CustomUser, username=username)
    context = {
        "user": user
    }
    template_name = "payment_information.html"
    return render(request, template_name, context)


# # WEBHOOKのシークレットキー
# endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


def create_card(request, username):
    user = get_object_or_404(CustomUser, username=username)
    # セッションを開始するため、STRIPEのシークレットキーをセットする
    stripe.api_key = settings.STRIPE_API_KEY

    # Customerオブジェクトを作成（引数は任意）
    stripe_customer = stripe.Customer.create(name=user.username)
    # SetupIntentオブジェクト生成
    setup_intent = stripe.SetupIntent.create(
        customer=stripe_customer.id,  # 生成したCustomerのIDを指定
        payment_method_types=["card"],  # 支払い方法→今回はクレジットカード（"card"）
    )
    # 作成したSetupIntentからclient_secretを取得する→テンプレートへ渡す
    context = {
        "client_secret": setup_intent.client_secret,
    }
    return render(request, "create_card.html", context)



def thanks(request):
    return render(request, "thanks.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def rules(request):
    return render(request, "rules.html")
