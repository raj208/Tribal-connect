from django.urls import path
from .views import artisan_detail, artisan_profile_edit, gallery_add

app_name = "artisans"

urlpatterns = [
    path("<str:username>/", artisan_detail, name="detail"),
    path("me/edit/", artisan_profile_edit, name="profile_edit"),
    path("me/gallery/add/", gallery_add, name="gallery_add"),
]
