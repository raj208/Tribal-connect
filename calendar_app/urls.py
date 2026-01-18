from django.urls import path
from .views import calendar_month_view, calendar_list_view, event_detail_view, event_create_view

app_name = "calendar_app"

urlpatterns = [
    path("", calendar_month_view, name="month"),
    path("list/", calendar_list_view, name="list"),
    path("create/", event_create_view, name="create"),
    path("<int:event_id>/", event_detail_view, name="detail"),
    
]
