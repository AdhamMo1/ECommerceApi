from django.contrib import admin
from django.conf import settings
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id','username','email','first_name','last_name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name','price','featured']    

@admin.register(Category)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','created_at','updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id','product','quantity','cart']   

@admin.register(ProductRating)
class ProductRating(admin.ModelAdmin):
    list_display = ['id','average_rating','total_reviews','product'] 


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ['id','customer','product','created_at'] 

admin.site.register([Order,OrderItem])              