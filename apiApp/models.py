from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings
# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_img = models.URLField(blank=True,null=True)

    def __str__(self):
        return self.email
    
class Customer(models.Model):
    address = models.CharField(null= True ,blank= True, max_length=100)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='customer',default=None)

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True,blank= True)
    img = models.ImageField(upload_to="media/category_img",blank=True,null=True) 

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    slug = models.SlugField(unique=True,blank=True)
    img = models.ImageField(upload_to="media/product_img",blank=True,null=True)
    featured = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,related_name='products',blank=True,null=True)

    def __str__(self):
        return self.name 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,related_name='cart',default=None)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product =models.ForeignKey(Product,on_delete=models.CASCADE,related_name='items')
    quantity = models.IntegerField(default=1)
        

class Review(models.Model):
    RATING_CHOICES = [
    (1, '1 - Poor'),
    (2, '2 - Fair'),
    (3, '3 - Good'),
    (4, '4 - Very Good'),
    (5, '5 - Excellent'),
    ]
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['customer','product']
        ordering = ['created_at']


class ProductRating(models.Model):
    product = models.OneToOneField(Product,on_delete=models.CASCADE,related_name='rating')
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default= 0)



class WishList(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='wishlists')
    product =  models.ForeignKey(Product,on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer','product']


class Order(models.Model):
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.stripe_checkout_id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order {self.product.name} - {self.order.stripe_checkout_id}"