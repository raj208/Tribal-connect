from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import moderator_required
from .forms import OpportunitySubmitForm
from .models import Opportunity
        
from django.db.models import Q

def opportunity_list_view(request):
    qs = Opportunity.objects.filter(status=Opportunity.Status.APPROVED)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(opportunity_type__icontains=q) |
            Q(location__icontains=q)
        )

    typ = (request.GET.get("type") or "").strip()
    if typ:
        qs = qs.filter(opportunity_type__icontains=typ)

    sort = request.GET.get("sort", "new")
    if sort == "deadline":
        qs = qs.order_by("deadline", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    context = {"opps": qs, "q": q, "typ": typ, "sort": sort}
    return render(request, "community/opportunities/list.html", context)



def opportunity_detail_view(request, opp_id: int):
    opp = get_object_or_404(Opportunity, id=opp_id)
    # Only show non-approved items to moderators/admin or the submitter
    if opp.status != Opportunity.Status.APPROVED:
        if not request.user.is_authenticated:
            return redirect("/login/")
        is_owner = opp.created_by_id == request.user.id
        is_mod = request.user.is_staff or request.user.is_superuser or request.user.groups.filter(name="Moderator").exists()
        if not (is_owner or is_mod):
            return redirect("opportunities:list")

    return render(request, "community/opportunities/detail.html", {"opp": opp})


@login_required
def opportunity_submit_view(request):
    if request.method == "POST":
        form = OpportunitySubmitForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.created_by = request.user
            opp.status = Opportunity.Status.PENDING
            opp.save()
            messages.success(request, "Opportunity submitted! It will be visible after Moderator/Admin approval.")
            return redirect("opportunities:list")
    else:
        form = OpportunitySubmitForm()

    return render(request, "community/opportunities/submit.html", {"form": form})


@moderator_required
def moderation_queue_view(request):
    pending = Opportunity.objects.filter(status=Opportunity.Status.PENDING).order_by("-created_at")
    rejected = Opportunity.objects.filter(status=Opportunity.Status.REJECTED).order_by("-created_at")[:50]
    context = {"pending": pending, "rejected": rejected}
    return render(request, "community/opportunities/mod_queue.html", context)


@moderator_required
def moderation_action_view(request, opp_id: int, action: str):
    opp = get_object_or_404(Opportunity, id=opp_id)

    if action not in ("approve", "reject"):
        messages.error(request, "Invalid action.")
        return redirect("opportunities:mod_queue")

    if action == "approve":
        opp.status = Opportunity.Status.APPROVED
        messages.success(request, "Opportunity approved.")
    else:
        opp.status = Opportunity.Status.REJECTED
        messages.success(request, "Opportunity rejected.")

    opp.reviewed_by = request.user
    opp.reviewed_at = timezone.now()
    opp.save(update_fields=["status", "reviewed_by", "reviewed_at"])

    return redirect("opportunities:mod_queue")
