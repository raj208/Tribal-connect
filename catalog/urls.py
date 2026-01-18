from django.urls import path
from .views import product_list, product_detail, my_products, product_create, product_edit, product_image_add

app_name = "catalog"

urlpatterns = [
    path("products/", product_list, name="product_list"),
    path("products/<int:pk>/", product_detail, name="product_detail"),
    path("my/products/", my_products, name="my_products"),
    path("my/products/new/", product_create, name="product_create"),
    path("my/products/<int:pk>/edit/", product_edit, name="product_edit"),
    path("my/products/<int:pk>/images/add/", product_image_add, name="product_image_add"),
]
