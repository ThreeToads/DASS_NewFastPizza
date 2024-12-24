from django.utils import timezone
from drf_spectacular.utils import extend_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import Clients, Managers, Drivers, User, ReadyForDeliveryOrder
from .serializers import RegisterSerializer, LoginSerializer, ReadyForDeliveryOrderSerializer, MarkAsDeliveredSerializer


class RegisterClientAPIView(APIView):
    """
    Регистрация пользователей сайта
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: {"description": "Пользователь успешно зарегистрирован"}},
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = 'client'  # Можно изменить на нужную роль
            user.save()

            # Добавляем пользователя в соответствующую таблицу
            # if user.role == 'client':
            #     Clients.objects.create(
            #         user=user,
            #         name=user.name,
            #         email=user.email,
            #         password=user.password,  # Храните пароль в хешированном виде!
            #     )
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
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
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email, is_staff=False)  # Только для клиентов
                if user.check_password(password):
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({"token": token.key}, status=status.HTTP_200_OK)
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginMenegerDriverAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
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
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                # Проверка на менеджеров и водителей (is_staff=True)
                user = User.objects.get(email=email, is_staff=True)
                if user.check_password(password):
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({"token": token.key}, status=status.HTTP_200_OK)
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReadyForDeliveryOrdersListView(ListAPIView):
    queryset = ReadyForDeliveryOrder.objects.filter(delivered_at__isnull=True)
    serializer_class = ReadyForDeliveryOrderSerializer  # permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        # Фильтруем только те заказы, которые ещё не доставлены
        return ReadyForDeliveryOrder.objects.filter(delivered_at__isnull=True)


# POST: Пометка заказа как доставленного
class MarkOrderAsDeliveredView(CreateAPIView):
    serializer_class = MarkAsDeliveredSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем данные из запроса
        order_id = serializer.validated_data['order_id']
        try:
            # Ищем заказ
            delivery_order = ReadyForDeliveryOrder.objects.get(order__id=order_id)

            # Проверяем, имеет ли водитель право на доставку этого заказа
            if delivery_order.driver and delivery_order.driver != request.user:
                return Response(
                    {"detail": "Вы не являетесь водителем для этого заказа."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Обновляем статус заказа
            delivery_order.driver = request.user
            delivery_order.delivered_at = timezone.now()
            delivery_order.save()

            return Response(
                {"detail": f"Заказ #{order_id} отмечен как доставленный."},
                status=status.HTTP_200_OK
            )
        except ReadyForDeliveryOrder.DoesNotExist:
            return Response(
                {"detail": "Заказ с указанным ID не найден или не готов к доставке."},
                status=status.HTTP_404_NOT_FOUND
            )