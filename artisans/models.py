from django.conf import settings
from django.db import models


class ArtisanProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artisan_profile",
    )

    # public info
    display_name = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    craft_style = models.CharField(max_length=160, blank=True)  # e.g., "Sohrai painting", "Bamboo craft"
    bio = models.TextField(blank=True)
    maker_story = models.TextField(blank=True)

    profile_photo = models.ImageField(upload_to="artisans/profile_photos/", blank=True, null=True)
    cover_photo = models.ImageField(upload_to="artisans/cover_photos/", blank=True, null=True)

    # ratings (we’ll update later from product reviews)
    rating_avg = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.display_name or self.user.username


class ArtisanGalleryImage(models.Model):
    artisan = models.ForeignKey(ArtisanProfile, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="artisans/gallery/")
    caption = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"GalleryImage({self.artisan_id})"
