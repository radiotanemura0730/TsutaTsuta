from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Product, Review
from decimal import Decimal
from django.db.models import Sum

def index(request):
    return render(request, 'index.html')

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
        average_rating = None
        subtract_rating = list(range(5))

    review_number = len(reviews)


    latest_user_products = user_products.order_by('-created_at')[:6]
    relatively_latest_user_products = user_products.order_by('-created_at')[6:12]

    context = {
        'user': user,
        'is_own_profile': is_own_profile,
        'latest_user_products': latest_user_products,
        'relatively_latest_user_products': relatively_latest_user_products,
        'average_rating': average_rate,
        'subtract_rating': subtract_rating,
        'review_number': review_number,
    }

    return render(request, 'profile.html', context)

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
        average_rating = None
        subtract_rating = list(range(5))

    review_number = len(reviews)

    total_profit = Product.objects.filter(seller=user).aggregate(Sum('price'))['price__sum'] or Decimal('0.0')

    # ポイントに関する機能は後で実装

    context = {
        'user': user,
        'average_rating': average_rate,
        'subtract_rating': subtract_rating,
        'review_number': review_number,
        'total_profit': total_profit,
    }

    return render(request, 'home_profile.html', context)

@login_required
def settings(request, username):

    user = get_object_or_404(CustomUser, username=username)   

    context = {
        'user': user,
    }
        
     

    return render(request, 'settings.html', context)




    





