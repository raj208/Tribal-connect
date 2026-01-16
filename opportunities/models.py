from django.conf import settings
from django.db import models


class Opportunity(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    # O2 decision: minimal required fields
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Optional fields (not required)
    opportunity_type = models.CharField(max_length=80, blank=True)  # scholarship/scheme/exhibition/etc
    source_link = models.URLField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    deadline = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submitted_opportunities")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_opportunities",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"
