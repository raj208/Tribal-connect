from django.db.models import Avg, Count

from artisans.models import ArtisanProfile
from .models import Review


def recompute_product_and_artisan(product):
    # Product aggregates
    p_agg = Review.objects.filter(product=product).aggregate(avg=Avg("rating"), count=Count("id"))
    product.rating_avg = float(p_agg["avg"] or 0.0)
    product.rating_count = int(p_agg["count"] or 0)
    product.save(update_fields=["rating_avg", "rating_count"])

    # Artisan aggregates (based on all reviews across all artisan products)
    artisan: ArtisanProfile = product.artisan
    a_agg = Review.objects.filter(product__artisan=artisan).aggregate(avg=Avg("rating"), count=Count("id"))
    artisan.rating_avg = float(a_agg["avg"] or 0.0)
    artisan.rating_count = int(a_agg["count"] or 0)
    artisan.save(update_fields=["rating_avg", "rating_count"])
