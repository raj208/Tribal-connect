from django.urls import path
from .views import checkout, success, my_orders, order_detail
from .views import artisan_orders, artisan_order_detail, artisan_item_update_status


app_name = "orders"

urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path("success/<int:order_id>/", success, name="success"),
    path("me/", my_orders, name="my_orders"),
    path("<int:order_id>/", order_detail, name="order_detail"),
    path("artisan/", artisan_orders, name="artisan_orders"),
    path("artisan/<int:order_id>/", artisan_order_detail, name="artisan_order_detail"),
    path("artisan/item/<int:item_id>/status/", artisan_item_update_status, name="artisan_item_update_status"),

]
