from django.contrib import admin
from .models import CustomUser, Product, Review, Comment, Like, Draft, Transaction, Class, Address

# Register your models here.
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.register(User)
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Draft)
admin.site.register(Transaction)
admin.site.register(Class)
admin.site.register(Address)
