from django.urls import path
from .views import (
    opportunity_list_view,
    opportunity_detail_view,
    opportunity_submit_view,
    moderation_queue_view,
    moderation_action_view,
)

app_name = "opportunities"

urlpatterns = [
    path("", opportunity_list_view, name="list"),
    path("submit/", opportunity_submit_view, name="submit"),
    path("mod/", moderation_queue_view, name="mod_queue"),
    path("mod/<int:opp_id>/<str:action>/", moderation_action_view, name="mod_action"),
    path("<int:opp_id>/", opportunity_detail_view, name="detail"),
]
