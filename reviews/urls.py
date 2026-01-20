from django.urls import path
from .views import review_create_or_edit

app_name = "reviews"

urlpatterns = [
    path("product/<int:product_id>/", review_create_or_edit, name="review_product"),
]
