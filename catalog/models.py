from django.db import models
from django.utils.text import slugify

from artisans.models import ArtisanProfile


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    artisan = models.ForeignKey(ArtisanProfile, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)  # INR
    is_made_to_order = models.BooleanField(default=True)
    production_time_days = models.PositiveIntegerField(default=7)  # ETA for made-to-order

    main_image = models.ImageField(upload_to="products/main/", blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    rating_avg = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)


    def __str__(self) -> str:
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/extra/")
    caption = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"ProductImage({self.product_id})"
