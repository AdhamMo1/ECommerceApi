from django.shortcuts import render,redirect
import stripe
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework import mixins,viewsets,filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import *
from .pagination import DefaultPagination
from .serializers import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


# This is your test secret API key.
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEBHOOK_SECRET

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    pagination_class = DefaultPagination
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description','category__name']
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailsSerializer
        elif self.action == 'list':
            return ProductListSerializer
        elif self.request.method == 'POST':
            return ProductCreateSerializer
        elif self.request.method == 'PUT':
            return ProductDetailsSerializer
        return ProductListSerializer 

    def retrieve(self, request, slug):
        product = Product.objects.get(slug = slug )
        serializer = ProductDetailsSerializer(product)
        return Response(serializer.data)
    

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    pagination_class = DefaultPagination
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailsSerializer
        elif self.action == 'list':
            return CategoryListSerializer
        return CategoryListSerializer 
    
    def retrieve(self, request, slug):
        category = Category.objects.get(slug = slug)
        serializer = CategoryDetailsSerializer(category)
        return Response(serializer.data)
    

class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT','PATCH']:
            return CartUpdateSerializer
        return CartSerializer
    

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class ProductRatingViewSet(mixins.RetrieveModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = ProductRating.objects.all()
    serializer_class = ProductRatingSerializer

class WishListViewSet(ModelViewSet):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer



YOUR_DOMAIN = 'http://127.0.0.1:8000/'
@api_view(['POST'])
def create_checkout_session(request):
    cart_id = request.data.get('cart')
    email = request.data.get('email')
    try:
        cart = Cart.objects.get(pk=cart_id)
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item.product.name},
                        'unit_amount': int(item.product.price * 100),
                    },
                    'quantity': item.quantity,
                }
                for item in cart.items.all()
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + 'success.html',
            cancel_url=YOUR_DOMAIN + 'cancel.html',
            metadata = {'cart_id': cart_id}
        )
        return Response({'url': checkout_session.url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if (
        event['type'] == 'checkout.session.completed'
        or event['type'] == 'checkout.session.async_payment_succeeded'
    ):
        session = event['data']['object']
        cart_id = session.get('metadata',{}).get('cart_id')
        fulfill_checkout(session,cart_id)
    return HttpResponse(status=200)    


def fulfill_checkout(session, cart_id):
    
    order = Order.objects.create(stripe_checkout_id=session["id"],
        amount=session["amount_total"],
        currency=session["currency"],
        customer_email=session["customer_email"],
        status="Paid")

    cart = Cart.objects.get(pk=cart_id)
    cartitems = cart.cartitems.all()

    for item in cartitems:
        orderitem = OrderItem.objects.create(order=order, product=item.product,quantity=item.quantity)
    
    cart.delete()


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer 