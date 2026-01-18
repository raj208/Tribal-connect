from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .forms import ArtisanProfileForm, GalleryImageForm
from .models import ArtisanProfile


def artisan_detail(request, username: str):
    user = get_object_or_404(User, username=username, role=User.Role.ARTISAN)
    # profile should exist via signal, but keep safe:
    profile, _ = ArtisanProfile.objects.get_or_create(user=user, defaults={"display_name": user.username})
    return render(request, "mart/artisans/profile_detail.html", {"profile": profile})


def _require_artisan(user) -> bool:
    return user.is_authenticated and user.role == User.Role.ARTISAN


@login_required
def artisan_profile_edit(request):
    if not _require_artisan(request.user):
        raise Http404("Not found")

    profile, _ = ArtisanProfile.objects.get_or_create(
        user=request.user, defaults={"display_name": request.user.username}
    )

    if request.method == "POST":
        form = ArtisanProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:dashboard")
    else:
        form = ArtisanProfileForm(instance=profile)

    gallery_form = GalleryImageForm()
    return render(
        request,
        "mart/artisans/profile_edit.html",
        {"form": form, "profile": profile, "gallery_form": gallery_form},
    )


@login_required
def gallery_add(request):
    if not _require_artisan(request.user):
        raise Http404("Not found")

    profile = get_object_or_404(ArtisanProfile, user=request.user)

    if request.method == "POST":
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.artisan = profile
            img.save()
    return redirect("artisans:profile_edit")
