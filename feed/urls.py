from django.urls import path
from .views import (
    post_list_view, post_create_view, post_detail_view, post_like_toggle_view,
    post_edit_view, post_delete_view, comment_delete_view,
    report_post_view, report_comment_view,
    mod_reports_view, mod_report_action_view,
)

app_name = "feed"

urlpatterns = [
    path("", post_list_view, name="post_list"),
    path("create/", post_create_view, name="post_create"),
    path("<int:post_id>/", post_detail_view, name="post_detail"),
    path("<int:post_id>/like/", post_like_toggle_view, name="post_like_toggle"),

    # edit/delete
    path("<int:post_id>/edit/", post_edit_view, name="post_edit"),
    path("<int:post_id>/delete/", post_delete_view, name="post_delete"),
    path("comment/<int:comment_id>/delete/", comment_delete_view, name="comment_delete"),

    # reporting
    path("<int:post_id>/report/", report_post_view, name="report_post"),
    path("comment/<int:comment_id>/report/", report_comment_view, name="report_comment"),

    # moderation
    path("mod/reports/", mod_reports_view, name="mod_reports"),
    path("mod/reports/<int:report_id>/action/", mod_report_action_view, name="mod_report_action"),
]
