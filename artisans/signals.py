from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from .models import ArtisanProfile


@receiver(post_save, sender=User)
def create_artisan_profile(sender, instance: User, created: bool, **kwargs):
    if created and instance.role == User.Role.ARTISAN:
        ArtisanProfile.objects.create(user=instance, display_name=instance.username)
