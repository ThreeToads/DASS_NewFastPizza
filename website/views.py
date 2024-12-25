from django.utils import timezone
from drf_spectacular.utils import extend_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework import serializers as src
from website import models
from website import serializers


class RegisterClientAPIView(APIView):
    """
    Регистрация пользователей сайта
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=serializers.RegisterSerializer,
        responses={201: {"description": "Пользователь успешно зарегистрирован"}},
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = 'client'
            user.set_password(serializer.validated_data['password'])
            user.save()

            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=serializers.LoginSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "token": openapi.Schema(type=openapi.TYPE_STRING, description="Token for authentication"),
                },
            ),
            400: openapi.Schema(type=openapi.TYPE_OBJECT, description="Validation errors"),
            401: openapi.Schema(type=openapi.TYPE_OBJECT, description="Invalid credentials"),
            404: openapi.Schema(type=openapi.TYPE_OBJECT, description="User not found"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = models.User.objects.get(email=email, is_staff=False)  # Только для клиентов
                if user.check_password(password):
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({"token": token.key}, status=status.HTTP_200_OK)
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            except models.User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginMenegerDriverAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=serializers.LoginSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "token": openapi.Schema(type=openapi.TYPE_STRING, description="Token for authentication"),
                },
            ),
            400: openapi.Schema(type=openapi.TYPE_OBJECT, description="Validation errors"),
            401: openapi.Schema(type=openapi.TYPE_OBJECT, description="Invalid credentials"),
            404: openapi.Schema(type=openapi.TYPE_OBJECT, description="User not found"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                # Проверка на менеджеров и водителей (is_staff=True)
                user = models.User.objects.get(email=email, is_staff=True)
                if user.check_password(password):
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({"token": token.key}, status=status.HTTP_200_OK)
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            except models.User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuViewSet(generics.ListAPIView):
    queryset = models.Menu.objects.all()
    serializer_class = serializers.MenuSerializer
    permission_classes = [IsAuthenticated]


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        menu_item_id = request.data.get('menu_item')
        quantity = request.data.get('quantity', 1)

        try:
            menu_item = models.Menu.objects.get(id=menu_item_id)
        except models.Menu.DoesNotExist:
            return Response({"detail": "Блюдо не найдено."}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = models.Cart.objects.get_or_create(user=user, menu_item=menu_item)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)

        cart_item.save()
        return Response(models.CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        models.Cart.objects.filter(user=request.user).delete()
        return Response({"detail": "Корзина очищена."}, status=status.HTTP_204_NO_CONTENT)


class EmptySerializer(src.Serializer):
    pass  # Пустой сериализатор


class CartTotalPriceView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    def get(self, request):
        user = request.user

        # Получаем все элементы корзины для данного пользователя
        cart_items = models.Cart.objects.filter(user=user)

        # Суммируем общую стоимость всех элементов корзины
        total_price = sum(item.total_price for item in cart_items)

        return Response({"total_price": total_price}, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'manager':
            return models.Order.objects.all()
        elif self.request.user.role == 'driver':
            return models.Order.objects.filter(is_ready_for_delivery=True, is_delivered=False)
        return models.Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = models.Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"detail": "Корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        order = models.Order.objects.create(user=user)
        order.items.set(cart_items)
        order.save()

        # Clear the cart after creating the order
        cart_items.delete()

        return Response(serializers.OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='ready')
    def mark_as_ready(self, request, pk=None):
        order = self.get_object()

        if request.user.role != 'manager':
            return Response({"detail": "Доступ запрещен."}, status=status.HTTP_403_FORBIDDEN)

        order.is_ready_for_delivery = True
        order.save()
        return Response({"detail": "Заказ готов к отправке."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='delivered')
    def mark_as_delivered(self, request, pk=None):
        order = self.get_object()

        if request.user.role != 'driver':
            return Response({"detail": "Доступ запрещен."}, status=status.HTTP_403_FORBIDDEN)

        order.is_delivered = True
        order.save()
        return Response({"detail": "Заказ отмечен как доставленный."}, status=status.HTTP_200_OK)
