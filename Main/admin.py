from django.contrib import admin
from .models import CustomUser, Product, Review, Comment, Like, Draft, Transaction, Class, Address

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Draft)
admin.site.register(Transaction)
admin.site.register(Class)
admin.site.register(Address)
