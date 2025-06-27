from rest_framework import serializers
from .models import *

class ProductListSerializer(serializers.ModelSerializer):
    img = serializers.ImageField()
    class Meta:
        model = Product
        fields = ['id','name','slug','img','price']

class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','description','slug','price','featured','category']

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','description','img','price','featured','category']

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','img','slug']
        read_only_fields = ['slug']     

class CategoryDetailsSerializer(serializers.ModelSerializer):
    products  = ProductListSerializer(many = True,read_only = True)
    class Meta:
        model = Category
        fields = ['id','name','slug','img','products']
        read_only_fields = ['slug']    


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductDetailsSerializer(read_only = True)
    quantity = serializers.IntegerField(read_only = False)
    sub_total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id','product','cart','quantity','sub_total']    

    def get_sub_total(self,cartitem):
        return cartitem.product.price * cartitem.quantity
    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many = True)
    cart_total = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(write_only = True)
    quantity = serializers.IntegerField(write_only = True)
    class Meta:
        model = Cart
        fields = ['id','created_at','updated_at','items','cart_total','product_id','quantity']
        read_only_fields = ['created_at','updated_at']    

    def get_cart_total(self,cart:Cart):
        total = 0
        for item in cart.items.all():
            total += item.product.price * item.quantity
        return total
            
    def create(self, validated_data):
        product_id = validated_data['product_id']
        product = Product.objects.filter(pk = product_id).first()

        customer,created = Customer.objects.get_or_create(user = self.context['request'].user)

        cart ,created = Cart.objects.get_or_create(customer = customer)

        cart_item = CartItem.objects.create(product = product,cart = cart,quantity = validated_data['quantity'])
        return cart

class CartUpdateSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many = True)
    class Meta:
        model = Cart
        fields = ['items']
    


class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id','total_quantity']  

    def get_total_quantity(self,cart:Cart):
        total = 0
        for item in cart.items:
            total += item.quantity
        return total
    

class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source = 'user.first_name')
    last_name = serializers.CharField(source = 'user.last_name')
    profile_img = serializers.ImageField(source = 'user.profile_img')
    class Meta:
        model = Customer
        fields = ['id','first_name','last_name','profile_img']    

class ReviewSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only = True)
    product = ProductDetailsSerializer(read_only = True)
    product_id = serializers.IntegerField(write_only = True)
    rating_display = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id','customer','product','product_id','rating', 'rating_display','review_message','created_at','updated_at']

    def get_rating_display(self, obj):
        return obj.get_rating_display()
    def create(self, validated_data):
        product_id = validated_data['product_id']
        product = Product.objects.filter(pk = product_id).first()

        user_id = self.context['request'].user
        customer , created = Customer.objects.get_or_create(user = user_id)

        review = Review.objects.create(customer = customer,product = product,rating = validated_data['rating'] , review_message = validated_data['review_message'])
        return review
    
class ProductRatingSerializer(serializers.ModelSerializer):
    product = ProductDetailsSerializer()
    class Meta:
        model = ProductRating
        fields = ['id','average_rating','total_reviews','product']    



class WishListSerializer(serializers.ModelSerializer):
    customer = serializers.IntegerField(source = 'customer_id' , read_only = True)
    class Meta:
        model = WishList
        fields = ['id','customer','product','created_at']
    def create(self, validated_data):
        customer , created = Customer.objects.get_or_create(user = self.context['request'].user)

        wish_list , created = WishList.objects.get_or_create(product = validated_data['product'],customer = customer)
        if created is False:
            raise serializers.ValidationError({'error' : 'You added this product to the wishlist before!'})
        return wish_list
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many =True , read_only = True)
    class Meta:
        model = Order
        fields = ['id','amount','currency','status','created_at','customer_email','items']