from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Perfil

User = settings.AUTH_USER_MODEL  # string not used here; we'll import actual model below

from django.contrib.auth import get_user_model
UserModel = get_user_model()

@receiver(post_save, sender=UserModel)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
