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
    menu_item_details = MenuSerializer(source='menu_item', read_only=True)

    class Meta:
        model = models.Cart
        fields = ['id', 'menu_item', 'quantity', 'menu_item_details']


class OrderSerializer(serializers.ModelSerializer):
    items_details = CartSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = models.Order
        fields = ['id', 'user', 'items', 'items_details', 'created_at', 'is_ready_for_delivery', 'is_delivered']


