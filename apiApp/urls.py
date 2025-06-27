from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *
from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()

router.register(r'products', ProductViewSet)
router.register(r'categories',CategoryViewSet)
router.register(r'carts',CartViewSet)
router.register(r'reviews',ReviewViewSet)
router.register(r'product-ratings',ProductRatingViewSet)
router.register(r'wishlists',WishListViewSet)
router.register(r'orders',OrderViewSet)
urlpatterns = [
    path('',include(router.urls)),
    path('create_checkout_session/',csrf_exempt(create_checkout_session),name='create_checkout_session'),
    path('webhook/',my_webhook_view,name='webhook')
]