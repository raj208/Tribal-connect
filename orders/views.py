from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import User
from cart.cart import clear, items, totals
from .forms import CheckoutForm
from .models import Order, OrderItem

from django.views.decorators.http import require_POST
from artisans.models import ArtisanProfile
from django.utils import timezone




def _require_customer(user):
    if not (user.is_authenticated and user.role == User.Role.CUSTOMER):
        raise Http404("Not found")


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    _require_customer(request.user)

    cart_items = items(request.session)
    subtotal, total_qty = totals(request.session)

    if total_qty == 0:
        return redirect("cart:detail")

    shipping_fee = Decimal(str(getattr(settings, "FLAT_SHIPPING_FEE", 0)))
    total = subtotal + shipping_fee

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                status=Order.Status.PENDING,
                full_name=form.cleaned_data["full_name"],
                phone=form.cleaned_data["phone"],
                address_line1=form.cleaned_data["address_line1"],
                address_line2=form.cleaned_data["address_line2"],
                city=form.cleaned_data["city"],
                state=form.cleaned_data["state"],
                pincode=form.cleaned_data["pincode"],
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                total=total,
            )

            for product, qty, _ in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    title=product.title,
                    price=product.price,
                    quantity=qty,
                )

            clear(request.session)
            return redirect("orders:success", order_id=order.id)
    else:
        form = CheckoutForm()

    return render(
        request,
        "mart/orders/checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping_fee": shipping_fee,
            "total": total,
        },
    )


@login_required
def success(request, order_id: int):
    _require_customer(request.user)
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id, user=request.user)
    return render(request, "mart/orders/success.html", {"order": order})


@login_required
def my_orders(request):
    _require_customer(request.user)
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "mart/orders/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id: int):
    _require_customer(request.user)
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id, user=request.user)
    return render(request, "mart/orders/order_detail.html", {"order": order})



def _require_artisan(user):
    if not (user.is_authenticated and user.role == User.Role.ARTISAN):
        raise Http404("Not found")


@login_required
def artisan_orders(request):
    _require_artisan(request.user)
    profile = get_object_or_404(ArtisanProfile, user=request.user)

    # show only PAID orders for now (you can include PENDING later if you want)
    items_qs = (
        OrderItem.objects
        .select_related("order", "order__user", "product")
        .filter(order__status=Order.Status.PAID, product__artisan=profile)
        .order_by("-order__created_at")
    )
    return render(request, "mart/orders/artisan_orders.html", {"items": items_qs})


@login_required
def artisan_order_detail(request, order_id: int):
    _require_artisan(request.user)
    profile = get_object_or_404(ArtisanProfile, user=request.user)

    # ensure this artisan has at least one item in this order
    if not OrderItem.objects.filter(order_id=order_id, product__artisan=profile).exists():
        raise Http404("Not found")

    order = get_object_or_404(Order.objects.select_related("user"), id=order_id, status=Order.Status.PAID)

    items_qs = (
        OrderItem.objects
        .select_related("product")
        .filter(order=order, product__artisan=profile)
        .order_by("id")
    )

    return render(request, "mart/orders/artisan_order_detail.html", {"order": order, "items": items_qs})

@login_required
@require_POST
def artisan_item_update_status(request, item_id: int):
    _require_artisan(request.user)
    profile = get_object_or_404(ArtisanProfile, user=request.user)

    item = get_object_or_404(
        OrderItem.objects.select_related("order", "product"),
        id=item_id,
        product__artisan=profile,
        order__status=Order.Status.PAID,
    )

    new_status = (request.POST.get("status") or "").strip()
    allowed = {c[0] for c in OrderItem.FulfillmentStatus.choices}
    if new_status not in allowed:
        return redirect("orders:artisan_order_detail", order_id=item.order_id)

    item.fulfillment_status = new_status

    # timestamps (simple MVP behavior)
    if new_status == OrderItem.FulfillmentStatus.SHIPPED and item.shipped_at is None:
        item.shipped_at = timezone.now()
    if new_status == OrderItem.FulfillmentStatus.DELIVERED and item.delivered_at is None:
        item.delivered_at = timezone.now()

    item.save(update_fields=["fulfillment_status", "shipped_at", "delivered_at", "updated_at"])
    return redirect("orders:artisan_order_detail", order_id=item.order_id)
