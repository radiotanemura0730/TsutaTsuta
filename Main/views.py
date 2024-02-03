from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Q, Subquery, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import UserProfileForm
from .models import Class, CustomUser, Product, Review, Transaction


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
def settings(request, username):
    user = get_object_or_404(CustomUser, username=username)

    context = {
        "user": user,
    }

    return render(request, "settings.html", context)


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
