from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class CulturalEvent(models.Model):
    class Category(models.TextChoices):
        FESTIVAL = "FESTIVAL", "Festival"
        WORKSHOP = "WORKSHOP", "Workshop"
        EXHIBITION = "EXHIBITION", "Exhibition"
        COMMUNITY = "COMMUNITY", "Community Event"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    category = models.CharField(max_length=20, choices=Category.choices)

    # Keep simple for MVP (you can add time later)
    date = models.DateField()
    location = models.CharField(max_length=120, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.date})"
