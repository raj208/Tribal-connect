from django.urls import path
from .views import pay_order, verify_payment, webhook

app_name = "payments"

urlpatterns = [
    path("pay/<int:order_id>/", pay_order, name="pay_order"),
    path("verify/<int:order_id>/", verify_payment, name="verify_payment"),
    path("webhook/", webhook, name="webhook"),  # optional safety
]
