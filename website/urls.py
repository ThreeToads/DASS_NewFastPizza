from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from website import views

router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'order', views.OrderViewSet, basename='order')
#router.register(r'menu', views.MenuViewSet, basename='menu')

urlpatterns = [
                  path('api/register/', views.RegisterClientAPIView.as_view(), name='register_client'),
                  path('api/login/', views.LoginAPIView.as_view(), name='login_client'),
                  path('api/login/staff/', views.LoginMenegerDriverAPIView.as_view(), name='login_staff'),
                  path('api/menu', views.MenuViewSet.as_view(), name='cart-total-price'),

                  path('cart_total/total_price/', views.CartTotalPriceView.as_view(), name='cart-total-price'),
                  path('cart/clear/', views.CartViewSet.as_view({'delete': 'clear_cart'}), name='cart-clear'),
                  path('api/order/', views.OrderViewSet.as_view({'get': 'list', 'post': 'create'}),
                       name='order-list-create'),  # Создание и получение заказов
                  path('api/order/<int:pk>/', views.OrderViewSet.as_view({'get': 'retrieve'}), name='order-detail'),
                  # Получение конкретного заказа
                  path('api/order/<int:pk>/ready/', views.OrderViewSet.as_view({'patch': 'mark_as_ready'}),
                       name='order-mark-ready'),  # Изменение статуса на "готов"
                  path('api/order/<int:pk>/delivered/', views.OrderViewSet.as_view({'patch': 'mark_as_delivered'}),
                       name='order-mark-delivered'),  # Изменение статуса на "доставлен"

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
