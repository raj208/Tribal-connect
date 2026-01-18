from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from artisans.models import ArtisanProfile
from .forms import ProductForm, ProductImageForm
from .models import Category, Product


def home(request):
    latest_products = (
        Product.objects.select_related("artisan", "artisan__user", "category")
        .filter(is_active=True)
        .order_by("-created_at")[:8]
    )
    categories = Category.objects.order_by("name")[:12]
    return render(request, "mart/home.html", {"latest_products": latest_products, "categories": categories})


def product_list(request):
    qs = (
        Product.objects.select_related("artisan", "artisan__user", "category")
        .filter(is_active=True)
        .order_by("-created_at")
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(title__icontains=q)

    cat = request.GET.get("category")
    if cat:
        qs = qs.filter(category__slug=cat)

    categories = Category.objects.order_by("name")
    return render(request, "mart/catalog/product_list.html", {"products": qs, "categories": categories, "q": q, "cat": cat})


def product_detail(request, pk: int):
    product = get_object_or_404(
        Product.objects.select_related("artisan", "artisan__user", "category").prefetch_related("images"),
        pk=pk,
        is_active=True,
    )
    from reviews.models import Review
    from orders.models import Order
    from accounts.models import User
    # return render(request, "catalog/product_detail.html", {"product": product})
    reviews = Review.objects.filter(product=product).select_related("user").order_by("-created_at")

    can_review = False
    if request.user.is_authenticated and request.user.role == User.Role.CUSTOMER:
        can_review = Order.objects.filter(
            user=request.user,
            status=Order.Status.PAID,
            items__product=product,
        ).exists()

        return render(request,"mart/catalog/product_detail.html",{"product": product, "reviews": reviews, "can_review": can_review},
        )

def _require_artisan(request):
    if not (request.user.is_authenticated and request.user.role == User.Role.ARTISAN):
        raise Http404("Not found")


@login_required
def my_products(request):
    _require_artisan(request)
    profile = get_object_or_404(ArtisanProfile, user=request.user)
    products = profile.products.order_by("-created_at")
    return render(request, "mart/catalog/my_products.html", {"products": products})


@login_required
def product_create(request):
    _require_artisan(request)
    profile = get_object_or_404(ArtisanProfile, user=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.artisan = profile
            product.save()
            return redirect("catalog:product_edit", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "mart/catalog/product_form.html", {"form": form, "mode": "create"})


@login_required
def product_edit(request, pk: int):
    _require_artisan(request)
    profile = get_object_or_404(ArtisanProfile, user=request.user)
    product = get_object_or_404(Product, pk=pk, artisan=profile)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("catalog:product_edit", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    image_form = ProductImageForm()
    return render(
        request,
        "mart/catalog/product_edit.html",
        {"form": form, "product": product, "image_form": image_form},
    )


@login_required
def product_image_add(request, pk: int):
    _require_artisan(request)
    profile = get_object_or_404(ArtisanProfile, user=request.user)
    product = get_object_or_404(Product, pk=pk, artisan=profile)

    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.product = product
            img.save()

    return redirect("catalog:product_edit", pk=product.pk)
