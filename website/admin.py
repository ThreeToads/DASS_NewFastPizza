from django.contrib import admin
from .models import Clients, Managers, Drivers, User, Menu, Cart, Order, ReadyForDeliveryOrder


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role')
    search_fields = ('name', 'email')
    list_filter = ['role']


@admin.register(Clients)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'password')
    search_fields = ('name', 'email')


@admin.register(Managers)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'password')
    search_fields = ('name', 'email')


@admin.register(Drivers)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'password')
    search_fields = ('name', 'email')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'image')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu_item', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'is_ready_for_delivery', 'is_delivered']
    list_filter = ['is_ready_for_delivery', 'is_delivered']


@admin.register(ReadyForDeliveryOrder)
class ReadyForDeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ['order', 'driver', 'delivered_at']
