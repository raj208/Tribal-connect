from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Review
from .services import recompute_product_and_artisan


@receiver(post_save, sender=Review)
def on_review_save(sender, instance: Review, **kwargs):
    recompute_product_and_artisan(instance.product)


@receiver(post_delete, sender=Review)
def on_review_delete(sender, instance: Review, **kwargs):
    recompute_product_and_artisan(instance.product)
