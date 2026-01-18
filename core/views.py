import datetime
from django.shortcuts import render

from feed.models import BasePost
from calendar_app.models import CulturalEvent
from opportunities.models import Opportunity


def home_view(request):
    today = datetime.date.today()

    # Latest posts (public only)
    latest_posts = (
        BasePost.objects.filter(is_hidden=False)
        .select_related("author")
        .prefetch_related("tags", "images")
        .order_by("-created_at")[:6]
    )

    # Upcoming events (today onwards)
    upcoming_events = (
        CulturalEvent.objects.filter(date__gte=today)
        .order_by("date", "id")[:6]
    )

    # Featured opportunities (deadline soon first; then newest)
    base_qs = Opportunity.objects.filter(status=Opportunity.Status.APPROVED)

    opps_with_deadline = base_qs.exclude(deadline__isnull=True).order_by("deadline", "-created_at")[:4]
    opps_no_deadline = base_qs.filter(deadline__isnull=True).order_by("-created_at")[:2]
    featured_opps = list(opps_with_deadline) + list(opps_no_deadline)

    context = {
        "latest_posts": latest_posts,
        "upcoming_events": upcoming_events,
        "featured_opps": featured_opps,
        "today": today,
    }
    return render(request, "community/core/home.html", context)
