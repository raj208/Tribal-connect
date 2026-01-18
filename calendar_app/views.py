from django.shortcuts import render

# Create your views here.
import calendar as pycal
import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import moderator_required
from .forms import CulturalEventForm
from .models import CulturalEvent


def _prev_month(year: int, month: int):
    if month == 1:
        return year - 1, 12
    return year, month - 1


def _next_month(year: int, month: int):
    if month == 12:
        return year + 1, 1
    return year, month + 1


def calendar_month_view(request):
    # default to current month
    today = datetime.date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # fetch events for this month
    events_qs = (
        CulturalEvent.objects.filter(date__year=year, date__month=month)
        .order_by("date", "id")
    )

    # map date -> list[events]
    events_by_day = {}
    for e in events_qs:
        events_by_day.setdefault(e.date, []).append(e)

    cal = pycal.Calendar(firstweekday=0)  # Monday=0 if you want, but Python uses 0=Monday? Actually 0=Monday in calendar module.
    # NOTE: In Python calendar, firstweekday=0 means Monday.
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        row = []
        for day in week:
            row.append({
                "date": day,
                "in_month": (day.month == month),
                "events": events_by_day.get(day, []),
                "is_today": (day == today),
            })
        weeks.append(row)

    prev_y, prev_m = _prev_month(year, month)
    next_y, next_m = _next_month(year, month)

    context = {
        "year": year,
        "month": month,
        "month_name": pycal.month_name[month],
        "weeks": weeks,
        "prev_year": prev_y,
        "prev_month": prev_m,
        "next_year": next_y,
        "next_month": next_m,
    }
    return render(request, "community/calendar_app/month.html", context)


def calendar_list_view(request):
    # Simple list view of upcoming events
    qs = CulturalEvent.objects.order_by("date", "id")

    cat = request.GET.get("cat", "")
    if cat in {c for c, _ in CulturalEvent.Category.choices}:
        qs = qs.filter(category=cat)

    context = {
        "events": qs,
        "categories": CulturalEvent.Category.choices,
        "selected_cat": cat,
    }
    return render(request, "community/calendar_app/list.html", context)


def event_detail_view(request, event_id: int):
    event = get_object_or_404(CulturalEvent, id=event_id)
    return render(request, "community/calendar_app/detail.html", {"event": event})


@moderator_required
def event_create_view(request):
    if request.method == "POST":
        form = CulturalEventForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.created_by = request.user
            ev.save()
            messages.success(request, "Event added to cultural calendar.")
            return redirect("calendar_app:month")
    else:
        form = CulturalEventForm()

    return render(request, "community/calendar_app/create.html", {"form": form})
