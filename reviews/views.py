from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from catalog.models import Product
from orders.models import Order
from .forms import ReviewForm
from .models import Review


def _require_customer(user):
    if not (user.is_authenticated and user.role == User.Role.CUSTOMER):
        raise Http404("Not found")


def _has_paid_purchase(user, product: Product) -> bool:
    return Order.objects.filter(
        user=user,
        status=Order.Status.PAID,
        items__product=product,
    ).exists()


@login_required
def review_create_or_edit(request, product_id: int):
    _require_customer(request.user)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if not _has_paid_purchase(request.user, product):
        raise Http404("You can only review products you purchased.")

    review, _ = Review.objects.get_or_create(product=product, user=request.user, defaults={"rating": 5})

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("catalog:product_detail", pk=product.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "mart/reviews/review_form.html", {"form": form, "product": product})
