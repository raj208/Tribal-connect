from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product
from .cart import add, remove, set_qty, items, totals


def cart_detail(request):
    cart_items = items(request.session)
    subtotal, total_qty = totals(request.session)
    return render(request, "mart/cart/cart_detail.html", {"cart_items": cart_items, "subtotal": subtotal, "total_qty": total_qty})


@require_POST
def cart_add(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    qty = int(request.POST.get("qty", 1))
    add(request.session, product.id, qty)
    messages.success(request, f"Added: {product.title}")
    return redirect("cart:detail")


@require_POST
def cart_remove(request, product_id: int):
    remove(request.session, product_id)
    messages.info(request, "Removed item from cart.")
    return redirect("cart:detail")


@require_POST
def cart_update(request, product_id: int):
    qty = int(request.POST.get("qty", 1))
    set_qty(request.session, product_id, qty)
    messages.info(request, "Cart updated.")
    return redirect("cart:detail")
