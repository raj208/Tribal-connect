import hmac
import json
import hashlib
from decimal import Decimal

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import User
from orders.models import Order


def _require_customer(user):
    if not (user.is_authenticated and user.role == User.Role.CUSTOMER):
        raise Http404("Not found")


def _client() -> razorpay.Client:
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise RuntimeError("Razorpay keys missing. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def pay_order(request, order_id: int):
    _require_customer(request.user)
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != Order.Status.PENDING:
        messages.info(request, "This order is not pending payment.")
        return redirect("orders:order_detail", order_id=order.id)

    # Amount in paise (integer)
    amount_paise = int((order.total * Decimal("100")).to_integral_value())

    # Create Razorpay order if missing
    if not order.razorpay_order_id:
        client = _client()
        rp_order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"tm_order_{order.id}",
                "notes": {"django_order_id": str(order.id)},
            }
        )
        order.razorpay_order_id = rp_order["id"]
        order.save(update_fields=["razorpay_order_id"])

    context = {
        "order": order,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_paise": amount_paise,
        "amount_rupees": order.total,
    }
    return render(request, "mart/payments/pay_order.html", context)


@login_required
@require_POST
def verify_payment(request, order_id: int):
    _require_customer(request.user)
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != Order.Status.PENDING:
        return redirect("orders:order_detail", order_id=order.id)

    payment_id = request.POST.get("razorpay_payment_id", "")
    signature = request.POST.get("razorpay_signature", "")

    if not (payment_id and signature and order.razorpay_order_id):
        messages.error(request, "Payment verification failed: missing fields.")
        return redirect("orders:order_detail", order_id=order.id)

    client = _client()
    params = {
        "razorpay_order_id": order.razorpay_order_id,  # use stored value (don’t trust client)
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature,
    }

    try:
        client.utility.verify_payment_signature(params)
    except Exception:
        messages.error(request, "Payment signature verification failed.")
        return redirect("orders:order_detail", order_id=order.id)

    # Mark paid
    order.status = Order.Status.PAID
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "razorpay_payment_id", "razorpay_signature", "paid_at"])

    messages.success(request, "Payment successful! Order marked as PAID.")
    return redirect("orders:order_detail", order_id=order.id)


@csrf_exempt
@require_POST
def webhook(request):
    """
    Optional: validates webhook signature using HMAC SHA256 with webhook secret. :contentReference[oaicite:2]{index=2}
    Then marks order as PAID when payment is captured.
    """
    secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", "")
    if not secret:
        return HttpResponse("Webhook secret not configured", status=400)

    received_sig = request.headers.get("X-Razorpay-Signature", "")
    body = request.body  # raw body

    expected_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(received_sig, expected_sig):
        return HttpResponse("Invalid signature", status=400)

    payload = json.loads(body.decode("utf-8"))
    event = payload.get("event")

    if event == "payment.captured":
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        rp_order_id = entity.get("order_id")
        rp_payment_id = entity.get("id")

        if rp_order_id and rp_payment_id:
            try:
                order = Order.objects.get(razorpay_order_id=rp_order_id)
                if order.status == Order.Status.PENDING:
                    order.status = Order.Status.PAID
                    order.razorpay_payment_id = rp_payment_id
                    order.paid_at = timezone.now()
                    order.save(update_fields=["status", "razorpay_payment_id", "paid_at"])
            except Order.DoesNotExist:
                pass

    return JsonResponse({"ok": True})
