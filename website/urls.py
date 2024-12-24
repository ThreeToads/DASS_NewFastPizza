from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import RegisterClientAPIView, LoginAPIView, LoginMenegerDriverAPIView, ReadyForDeliveryOrdersListView, \
    MarkOrderAsDeliveredView

urlpatterns = [
                  path('api/register/', RegisterClientAPIView.as_view(), name='register_client'),
                  path('api/login/', LoginAPIView.as_view(), name='login_client'),
                  path('api/login/staff/', LoginMenegerDriverAPIView.as_view(), name='login_staff'),
                  path('delivery/orders/', ReadyForDeliveryOrdersListView.as_view(), name='delivery-orders-list'),
                  path('delivery/mark-as-delivered/', MarkOrderAsDeliveredView.as_view(), name='mark-order-as-delivered'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
