from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.db.models import Avg
from ..models import *

@receiver(post_save,sender = Review)
def create_avr_reviews_for_product(sender,**kwargs):
    if kwargs['created']:
        total_reviews = Review.objects.filter(product = kwargs['instance'].product).count()
        avg_rating = round(Review.objects.filter(product = kwargs['instance'].product).aggregate(Avg('rating'))['rating__avg'],1) or 0.0
        product_rating,created = ProductRating.objects.get_or_create(product = kwargs['instance'].product)
        product_rating.average_rating = avg_rating
        product_rating.total_reviews = total_reviews
        product_rating.save()

@receiver(post_delete,sender = Review)
def on_delete_review_of_product(sender,instance,**kwargs):
    product = instance.product
    reviews = product.reviews.all()
    total = reviews.count()

    avg_rating = round(reviews.filter(product = product).aggregate(Avg('rating'))['rating__avg'],1) or 0.0

    product_rating , created = ProductRating.objects.get_or_create(product = product)
    product_rating.total_reviews = total
    product_rating.average_rating = avg_rating
    product_rating.save()