from django.db.models.signals import post_save
from django.dispatch import receiver

from website.models import User, Clients, Drivers, Managers


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Создаем профиль в зависимости от роли
        if instance.role == 'client':
            Clients.objects.create(user=instance, name=instance.name, email=instance.email)
        elif instance.role == 'manager':
            Managers.objects.create(user=instance, name=instance.name, email=instance.email)
        elif instance.role == 'driver':
            Drivers.objects.create(user=instance, name=instance.name, email=instance.email)
    else:
        # Обновляем или переносим профиль, если роль изменилась
        Clients.objects.filter(user=instance).delete()
        Managers.objects.filter(user=instance).delete()
        Drivers.objects.filter(user=instance).delete()

        if instance.role == 'client':
            Clients.objects.create(user=instance, name=instance.name, email=instance.email)
        elif instance.role == 'manager':
            Managers.objects.create(user=instance, name=instance.name, email=instance.email)
        elif instance.role == 'driver':
            Drivers.objects.create(user=instance, name=instance.name, email=instance.email)

# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, **kwargs):
#     # Проверяем, изменяется ли роль пользователя
#     if instance.role == 'driver':
#         Managers.objects.filter(user=instance).delete()
#         Clients.objects.filter(user=instance).delete()
#         # Проверяем, существует ли профиль водителя, если нет, создаем
#         if not Drivers.objects.filter(user=instance).exists():
#             Drivers.objects.update_or_create(
#                 user=instance,
#                 name=instance.name,
#                 email=instance.email,
#                 password=instance.password,  # Хеширование пароля!
#             )
#     elif instance.role == 'manager':
#         # Проверяем, существует ли профиль manager, если нет, создаем
#         Drivers.objects.filter(user=instance).delete()
#         Clients.objects.filter(user=instance).delete()
#         if not Managers.objects.filter(user=instance).exists():
#             Managers.objects.update_or_create(
#                 user=instance,
#                 name=instance.name,
#                 email=instance.email,
#                 password=instance.password,  # Хеширование пароля!
#             )
#     # elif instance.role == 'client':
#     #     # Проверяем, существует ли профиль manager, если нет, создаем
#     #     Drivers.objects.filter(user=instance).delete()
#     #     Managers.objects.filter(user=instance).delete()
#     #     if not Clients.objects.filter(user=instance).exists():
#     #         Clients.objects.update_or_create(
#     #             user=instance,
#     #             name=instance.name,
#     #             email=instance.email,
#     #             password=instance.password,
#     #         )  # Хеширование пароля!
