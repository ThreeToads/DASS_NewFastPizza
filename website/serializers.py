from rest_framework import serializers
from .models import User, ReadyForDeliveryOrder


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ReadyForDeliveryOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadyForDeliveryOrder
        fields = ['id', 'order', 'driver', 'delivered_at']


class MarkAsDeliveredSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
