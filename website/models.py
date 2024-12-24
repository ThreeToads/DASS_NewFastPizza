from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=[('client', 'Client'), ('manager', 'Manager'), ('driver', 'Driver')])

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


class Clients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', default=None)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.name


class Managers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile', default=None)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'

    def __str__(self):
        return self.name


class Drivers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile', default=None)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название блюда",
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
    )
    image = models.ImageField(
        upload_to='menu_photos/',
        verbose_name="Фотография блюда",
    )

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Меню"

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="Пользователь",
    )
    menu_item = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Блюдо",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"{self.user.email} - {self.menu_item.name} (x{self.quantity})"


class Order(models.Model):
    user = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Пользователь",
    )
    items = models.ManyToManyField(
        Cart,
        related_name='orders',
        verbose_name='Содержимое заказа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    is_ready_for_delivery = models.BooleanField(
        default=False,
        verbose_name="Готов к отправке",
    )
    is_delivered = models.BooleanField(
        default=False,
        verbose_name="Доставлен",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.email}"


class ReadyForDeliveryOrder(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='ready_for_delivery',
        verbose_name="Заказ",
    )
    driver = models.ForeignKey(
        Drivers,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries',
        verbose_name="Водитель",
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата доставки",
    )

    class Meta:
        verbose_name = "Готовый к доставке заказ"
        verbose_name_plural = "Готовые к доставке заказы"

    def __str__(self):
        return f"Готовый к доставке заказ #{self.order.id}"