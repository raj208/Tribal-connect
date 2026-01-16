from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import RegisterForm
from .models import User


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()   # <- use the form’s save()
            login(request, user)
            return redirect(request.GET.get("next") or "accounts:dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


# Alias to keep your community URL working if it used signup_view
def signup_view(request):
    return register(request)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    next_url = request.GET.get("next") or ""

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.POST.get("next") or "accounts:dashboard")
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": next_url},
    )


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def dashboard(request):
    if request.user.role == User.Role.ARTISAN:
        return render(request, "accounts/dashboard_artisan.html")
    return render(request, "accounts/dashboard_customer.html")
