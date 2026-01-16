from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        ARTISAN = "ARTISAN", "Artisan"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    def is_artisan(self) -> bool:
        return self.role == self.Role.ARTISAN

    def is_customer(self) -> bool:
        return self.role == self.Role.CUSTOMER


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile({self.user.username})"


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def ensure_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     else:
#         # safety: if a user existed without profile
#         Profile.objects.get_or_create(user=instance)
