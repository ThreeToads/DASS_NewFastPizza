from rest_framework import serializers
from website import models


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('name', 'email', 'password')

    def create(self, validated_data):
        user = models.User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Menu
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = models.Cart
        fields = ['menu_item', 'quantity', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = CartSerializer(many=True)

    class Meta:
        model = models.Order
        fields = ['id', 'user', 'items', 'created_at', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = models.Order.objects.create(**validated_data)
        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            cart_item, created = models.Cart.objects.get_or_create(user=order.user, menu_item=menu_item)
            cart_item.quantity += quantity
            cart_item.save()
            order.items.add(cart_item)
        order.save()
        return order

