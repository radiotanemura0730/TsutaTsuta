import random
from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.mail import send_mail
from django.db.models import OuterRef, Q, Subquery, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, RedirectView, TemplateView, UpdateView

from .forms import (
    AvailableProductsForm,
    CommentForm,
    CustomAuthenticationForm,
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

stripe.api_key = settings.STRIPE_API_KEY


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
                return render(
                    request,
                    self.template_name,
                    {
                        "pk": pk,
                        "form": form,
                        "user_email": user.email,
                        "error_message": "認証番号が正しくありません",
                    },
                )
        else:
            return render(
                request,
                self.template_name,
                {"pk": pk, "form": form, "error_message": "入力が正しくありません"},
            )


class SignupResendEmailView(RedirectView):
    permanent = False
    pattern_name = "signup_auth"

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs["pk"]
        user = CustomUser.objects.get(id=pk)
        to_email = user.email
        random_number_str = str(user.auth_number)
        subject = "題名"
        message = "認証番号の" + random_number_str + "を入力してください"
        from_email = "system@example.com"
        recipient_list = [to_email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return reverse_lazy(self.pattern_name, kwargs={"pk": pk})


class SignUpDoneView(UpdateView):
    template_name = "Main/signup_done.html"
    model = CustomUser
    fields = ("user_id", "username")
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user_id = form.cleaned_data["user_id"]
        if CustomUser.objects.filter(user_id=user_id).exists():
            return render(
                self.request,
                self.template_name,
                {
                    "pk": self.object.id,
                    "form": form,
                    "error_message_2": "このユーザーIDはすでに使用されています。",
                },
            )
        response = super().form_valid(form)
        CustomUser.objects.filter(pk=self.object.pk).update(
            user_id=form.cleaned_data["user_id"]
        )
        CustomUser.objects.filter(pk=self.object.pk).update(
            user_id=form.cleaned_data["username"]
        )
        user = CustomUser.objects.get(pk=self.object.pk)
        login(self.request, user)
        return response

    def form_invalid(self, form):
        return render(
            self.request,
            self.template_name,
            {
                "pk": self.object.id,
                "form": form,
                "error_message_1": "このユーザー名はすでに使用されています。",
            },
        )


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "Main/login.html"
    redirect_authenticated_user = True


class CustomPasswordResetView(PasswordResetView):
    template_name = "Main/password_reset.html"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        if not CustomUser.objects.filter(email=email).exists():
            form.add_error("email", "このメールアドレスは登録されていません。")
            return self.form_invalid(form)
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "Main/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "Main/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "Main/password_reset_complete.html"


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
def all_product_profile(request, username):
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

    context = {
        "user": user,
        "is_own_profile": is_own_profile,
        "average_rating": average_rate,
        "subtract_rating": subtract_rating,
        "review_number": review_number,
        "user_products": user_products,
    }

    return render(request, "all_product_profile.html", context)


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
            new_username = user_form.cleaned_data["username"]
            return redirect(reverse("home_profile", args=[new_username]))

    else:
        user_form = UserProfileForm(instance=user)

    context = {"user_form": user_form, "username": username}

    return render(request, "edit_profile.html", context)


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
        return redirect("delete_confirm")

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

    context = {
        "user_form": user_form,
        "user": user,
    }
    return render(request, "edit_address.html", context)


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
    product = get_object_or_404(Product, id=product_id)
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
    return render(request, "payment_information.html", context)


# # WEBHOOKのシークレットキー
# endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


def create_card(request, username):
    user = get_object_or_404(CustomUser, username=username)
    stripe_customer = stripe.Customer.create(
        name=user.username,
    )
    setup_intent = stripe.SetupIntent.create(
        customer=stripe_customer.id,  # 生成したCustomerのIDを指定
        payment_method_types=["card"],
    )
    context = {
        "client_secret": setup_intent.client_secret,
    }
    return render(request, "create_card.html", context)


def thanks(request):
    return render(request, "thanks.html")


def privacy_policy(request, username):
    user = get_object_or_404(CustomUser, username=username)

    context = {"user": user}

    return render(request, "privacy_policy.html", context)


def rules(request, username):
    user = get_object_or_404(CustomUser, username=username)

    context = {"user": user}

    return render(request, "rules.html", context)


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


def payment(request, username):
    user = get_object_or_404(CustomUser, username=username)
    address = Address.objects.filter(user=user)
    customer_id = user.stripe_customer_id  # CustomerオブジェクトIDを格納するフィールド名（任意）
    price = 2000
    card_list = stripe.Customer.list_payment_methods(
        customer_id,  # CustomerオブジェクトID
        type="card",
    )
    context = {
        "user": user,
        "address": address[0],
        "price": price,
        "card_list": card_list,
    }
    return render(request, "payment.html", context)


def payment_post(request):
    user = request.user
    customer_id = user.stripe_customer_id

    stripe_card = stripe.Customer.list_payment_methods(
        customer_id,
        type="card",
    )

    # 今回はStripeからのカード情報の取得順によって、支払いに使用するカードを指定する
    card_number = request.POST.get("card_number")
    selected_card = stripe_card["data"][int(card_number)]["id"]
    amount = request.POST.get("amount")

    # これで支払の処理を完了する
    stripe.PaymentIntent.create(
        amount=amount,  # 支払金額
        currency="jpy",  # 利用通貨
        customer=customer_id,  # CustomerオブジェクトID
        payment_method=selected_card,  # 支払いに使用するクレジットカード
        off_session=True,  # 支払いの実行時に顧客が決済フローに存在しないことを示す
        confirm=True,  # PaymentIntentの作成と確認を同時に行う
    )
    # PaymentIntentオブジェクトIDをDBに保存する場合は、「payment_intent.id」をsave()でDB保存する

    return redirect("payment_complete")


def payment_complete(request):
    return render(request, "payment_complete.html")


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


class LogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy("login")
