import random
from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, SignUpForm, SignUpAuthForm, AvailableProductsForm, OnTransactionProductsForm, CustomAuthenticationForm
from .models import Class, CustomUser, Product, Review, Transaction, Like
from django.views.generic import CreateView, TemplateView, UpdateView, RedirectView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import send_mail
from django.db.models import OuterRef, Q, Subquery, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import (
    AvailableProductsForm,
    CommentForm,
    OnTransactionProductsForm,
    SellForm,
    SignUpAuthForm,
    SignUpForm,
    UserAddressForm,
    UserProfileForm,
)
from .models import (
    Address,
    Class,
    Comment,
    CustomUser,
    Like,
    Product,
    Review,
    Transaction,
)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "Main/signup.html"

    def form_valid(self, form):
        super().form_valid(form)
        random_number = random.randint(1000, 9999)
        random_number_str = str(random_number)
        to_email = form.cleaned_data["email"]
        subject = "題名"
        message = "認証番号の" + random_number_str + "を入力してください"
        from_email = "system@example.com"
        recipient_list = [to_email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        user_record = CustomUser.objects.get(email=to_email)
        user_record.auth_number = random_number
        user_record.save()
        self.pk = int(user_record.id)
        return redirect("signup_auth", pk=self.object.id)

    def get_success_url(self) -> str:
        return reverse_lazy("signup_auth", kwargs={"pk": self.object.id})


class SignUpAuthView(TemplateView):
    template_name = "Main/signup_auth.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs["pk"]
        user = CustomUser.objects.get(id=pk)
        context["user_email"] = user.email
        context["pk"] = pk
        context["form"] = SignUpAuthForm()
        return context

    def post(self, request, pk):
        form = SignUpAuthForm(request.POST)
        if form.is_valid():
            entered_auth_number = form.cleaned_data["auth_number"]
            user = CustomUser.objects.get(id=pk)
            saved_auth_number = user.auth_number
            if entered_auth_number == saved_auth_number:
                return redirect("signup_done", pk=pk)
            else:
                return render(request, self.template_name, {'pk': pk, 'form': form, 'user_email':user.email,'error_message': '認証番号が正しくありません'})
        else:
            return render(
                request,
                self.template_name,
                {"pk": pk, "form": form, "error_message": "入力が正しくありません"},
            )

class SignupResendEmailView(RedirectView):
    permanent = False
    pattern_name = 'signup_auth'

    def get_redirect_url(self,*args, **kwargs):
        pk = self.kwargs['pk']
        user = CustomUser.objects.get(id=pk)
        to_email = user.email
        random_number_str = str(user.auth_number)
        subject = "題名"
        message = "認証番号の" + random_number_str + "を入力してください"
        from_email = "system@example.com"
        recipient_list = [to_email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return reverse_lazy(self.pattern_name, kwargs={'pk': pk})

class SignUpDoneView(UpdateView):
    template_name = "Main/signup_done.html"
    model = CustomUser
    fields = ("user_id",)
    success_url = reverse_lazy("home")

    def form_valid(self,form):
        user_id = form.cleaned_data['user_id']
        if CustomUser.objects.filter(user_id=user_id).exists():
            return render(self.request, self.template_name, {'pk': self.object.id, 'form': form, 'error_message': 'このユーザーIDはすでに使用されています。'})
        response = super().form_valid(form)
        CustomUser.objects.filter(pk=self.object.pk).update(
            user_id=form.cleaned_data["user_id"]
        )
        user = CustomUser.objects.get(pk=self.object.pk)
        login(self.request, user)
        return response
    
class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'Main/login.html'

class CustomPasswordResetView(PasswordResetView):
    template_name = 'Main/password_reset.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'Main/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'Main/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'Main/password_reset_complete.html'


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
    return render(request, "edit_address.html", {"user_form": user_form})


@login_required
def home_view(request):
    user = get_object_or_404(CustomUser, pk=request.user.pk)
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
    return render(request, "home.html", context)


@login_required
def product_description(request, product_id):
    user = get_object_or_404(CustomUser, pk=request.user.pk)
    form = CommentForm()
    product = Product.objects.get(id=product_id)
    if Review.objects.filter(user=product.seller).exists():
        review = Review.objects.get(user=product.seller)
    else:
        review = None
    if Transaction.objects.filter(product=product).exists():
        transaction = Transaction.objects.filter(product=product)
    else:
        transaction = None
    time = timezone.now()
    comment = Comment.objects.filter(product=product).order_by("-created_date")
    comment_length = len(comment)
    address = Address.objects.get(user=product.seller)
    transaction_exists = Transaction.objects.filter(
        product_id=OuterRef("pk"), buyer__isnull=False
    ).values("product_id")[:1]
    products_list = (
        Product.objects.exclude(
            Q(seller=user) | Q(pk__in=Subquery(transaction_exists)) | Q(pk=product.pk)
        )
        .filter(gakka_category=product.gakka_category)
        .filter(genre=product.genre)
    )
    if Like.objects.filter(user=user, product=product).exists():
        is_user_like = True
    else:
        is_user_like = False
    context = {
        "user": user,
        "product": product,
        "review": review,
        "transaction": transaction,
        "time": time,
        "comment_list": comment,
        "comment_length": comment_length,
        "address": address,
        "others": products_list,
        "form": form,
        "is_user_like": is_user_like,
    }

    if request.POST:
        new_comment = Comment(user=user, product=product)
        form = CommentForm(request.POST, instance=new_comment)
        if form.is_valid():
            form.save()
            return redirect("product_description", product_id)
        else:
            print(form.errors)

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


@login_required
def exhibited_products(request, username):
    user = get_object_or_404(CustomUser, username=username)

    exhibited_products = Product.objects.filter(seller=user)

    trading_products = Transaction.objects.filter(seller=user)

    sold_products = trading_products.filter(is_received=True)

    trading_products = trading_products.difference(sold_products)

    trading_products = [transaction.product for transaction in trading_products]

    sold_products = [transaction.product for transaction in sold_products]

    context = {
        "user": user,
        "exhibited_products": exhibited_products,
        "trading_products": trading_products,
        "sold_products": sold_products,
    }

    return render(request, "exhibited_products.html", context)


def payment_information(request, username):
    user = get_object_or_404(CustomUser, username=username)
    context = {"user": user}
    template_name = "payment_information.html"
    return render(request, template_name, context)


# # WEBHOOKのシークレットキー
# endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
@require_POST
def create_card(request, username):
    user = get_object_or_404(CustomUser, username=username)
    domain = "https://127.0.0.1:8000"
    # 開発状態ではこのドメインを使用
    if settings.DEBUG:
        domain = "http://127.0.0.1:8000"
    # セッションを開始するため、STRIPEのシークレットキーをセットする
    stripe.PaymentMethodDomain.create(domain_name=domain)
    # Customerオブジェクトを作成（引数は任意）
    stripe_customer = stripe.Customer.create(name=user.username)
    print(stripe_customer.id)
    print(stripe_customer.name)
    # SetupIntentオブジェクト生成
    # カードの支払い情報を顧客に登録する
    session = stripe.checkout.Session.create(
        customer=stripe_customer.id,
        payment_method_types=["card"],
        mode="setup",
        client_reference_id=request.user.id,
        success_url="https://example.com/checkout/return?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://exaple.com/checkout/cancel",
    )
    print(session)
    # Stripeセッションを取得
    stripe_session = stripe.checkout.Session.retrieve(session.id)
    setup_intent_id = stripe_session.setup_intent
    return JsonResponse(
        {"clientSecret": session.client_secret, "setupIntentId": setup_intent_id}
    )


def create_card2(request, username):
    current_customer = get_object_or_404(CustomUser, username=username)
    # Save stripe customer infor
    if not current_customer.stripe_customer_id:
        customer = stripe.Customer.create()
        current_customer.stripe_customer_id = customer["id"]
        current_customer.save()
    # Get Stripe payment method
    stripe_payment_methods = stripe.PaymentMethod.list(
        customer=current_customer.stripe_customer_id,
        type="card",
    )
    print(stripe_payment_methods)
    if stripe_payment_methods and len(stripe_payment_methods.data) > 0:
        payment_method = stripe_payment_methods.data[0]
        current_customer.stripe_payment_method_id = payment_method.id
        current_customer.stripe_card_last4 = payment_method.card.last4
        current_customer.save()
    else:
        current_customer.stripe_payment_method_id = ""
        current_customer.stripe_card_last4 = ""
        current_customer.save()
    # SetupIntentオブジェクト生成
    intent = stripe.SetupIntent.create(customer=current_customer.stripe_customer_id)
    return render(
        request,
        "create_card2.html",
        {
            "client_secret": intent.client_secret,
            "STRIPE_API_PUBLIC_KEY": settings.STRIPE_API_PUBLIC_KEY,
        },
    )


def thanks(request):
    return render(request, "thanks.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def rules(request):
    return render(request, "rules.html")


def like_product(request):
    product_pk = request.POST.get("product_pk")
    context = {
        "user": request.user.id,
    }
    product = get_object_or_404(Product, pk=product_pk)
    like = Like.objects.filter(product=product, user=request.user)
    if like.exists():
        like.delete()
        context["method"] = "delete"
    else:
        like.create(product=product, user=request.user)
        context["method"] = "create"

    return JsonResponse(context)


def before_payment(request, username):
    user = get_object_or_404(CustomUser, username=username)
    address = Address.objects.filter(user=user)
    print(address[0].last_name)
    context = {
        "user": user,
        "address": address[0],
    }
    return render(request, "before_payment.html", context)


def after_payment(request):
    return render(request, "before_payment.html")


@login_required
def sell(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    if Address.objects.filter(user=user).exists():
        address = Address.objects.get(user=user)
    else:
        address = None
    form = SellForm()
    if "confirm" in request.POST:
        form = SellForm(request.POST, request.FILES)
        if form.is_valid():
            product = Product()
            lecture_name = form.cleaned_data["lecture"]
            lecture_instance, _ = Class.objects.get_or_create(lecture=lecture_name)
            product.classroom_category = lecture_instance
            product.image = request.FILES["image"]
            product.product_name = request.POST["product_name"]
            product.gakubu_category = request.POST["gakubu_category"]
            product.gakka_category = request.POST["gakka_category"]
            product.genre = request.POST["genre"]
            product.condition = request.POST["condition"]
            product.description = request.POST["description"]
            product.responsibility = request.POST["responsibility"]
            product.price = request.POST["price"]
            product.seller = user
            product.save()
            return redirect("home")
        else:
            print(form.errors)
    elif "draft" in request.POST:
        # 下書きを保存する処理
        print("下書き保存")
    elif "delete" in request.POST:
        # 下書きを削除する処理
        print("下書き削除")
    context = {
        "user": user,
        "form": form,
        "address": address,
    }
    return render(request, "sell.html", context)


def temporary(request):
    return render(request, "temporary.html")
