from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from website.models import User, Clients, Drivers, Managers


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, **kwargs):
    # Проверяем, изменяется ли роль пользователя
    if instance.role == 'driver':
        Managers.objects.filter(user=instance).delete()
        Clients.objects.filter(user=instance).delete()
        Drivers.objects.update_or_create(user=instance, defaults={'name': instance.name, 'email': instance.email})
    elif instance.role == 'manager':
        Drivers.objects.filter(user=instance).delete()
        Clients.objects.filter(user=instance).delete()
        Managers.objects.update_or_create(user=instance, defaults={'name': instance.name, 'email': instance.email})
    elif instance.role == 'client':
        Drivers.objects.filter(user=instance).delete()
        Managers.objects.filter(user=instance).delete()
        Clients.objects.update_or_create(user=instance, defaults={'name': instance.name, 'email': instance.email})
