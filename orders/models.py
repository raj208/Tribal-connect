from decimal import Decimal
from django.conf import settings
from django.db import models

from catalog.models import Product
from django.utils import timezone



class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Payment"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Shipping address
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    pincode = models.CharField(max_length=10)

    # money snapshot
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)

    #payment
    razorpay_order_id = models.CharField(max_length=80, blank=True)
    razorpay_payment_id = models.CharField(max_length=80, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)



    def __str__(self) -> str:
        return f"Order#{self.id} - {self.user.username} - {self.status}"



class OrderItem(models.Model):
    class FulfillmentStatus(models.TextChoices):
        PLACED = "PLACED", "Placed"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    title = models.CharField(max_length=160)  # snapshot
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot
    quantity = models.PositiveIntegerField(default=1)

    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # ✅ NEW: fulfillment tracking per item
    fulfillment_status = models.CharField(
        max_length=20,
        choices=FulfillmentStatus.choices,
        default=FulfillmentStatus.PLACED,
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

