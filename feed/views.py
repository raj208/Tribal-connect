from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.db.models import Q
from .models import Tag


from accounts.utils import is_moderator
from accounts.decorators import moderator_required

from .forms import BasePostForm, CommentForm, ReportForm
from .models import (
    AnnouncementPost,
    BasePost,
    Comment,
    EducationPost,
    FestivalPost,
    FolktalePost,
    OralHighlightPost,
    PostImage,
    PostLike,
    Report,
)


TYPE_MODEL_MAP = {
    BasePost.PostType.FOLKTALE: FolktalePost,
    BasePost.PostType.FESTIVAL: FestivalPost,
    BasePost.PostType.EDUCATION: EducationPost,
    BasePost.PostType.ORAL: OralHighlightPost,
    BasePost.PostType.ANNOUNCEMENT: AnnouncementPost,
}


def _owner_or_mod_required(user, owner_id: int) -> bool:
    return user.is_authenticated and (user.id == owner_id or is_moderator(user))


def post_list_view(request):
    qs = BasePost.objects.filter(is_hidden=False).order_by("-created_at")

    # type filter
    selected_type = request.GET.get("type", "")
    valid_types = {t for t, _ in BasePost.PostType.choices}
    if selected_type in valid_types:
        qs = qs.filter(post_type=selected_type)
    else:
        selected_type = ""

    # tag filter
    selected_tag = (request.GET.get("tag") or "").strip().lower()
    if selected_tag:
        qs = qs.filter(tags__name__iexact=selected_tag)

    # keyword search
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(body__icontains=q) |
            Q(author__username__icontains=q)
        )

    qs = qs.distinct()

    # show top tags (simple)
    top_tags = Tag.objects.order_by("name")[:50]

    return render(
        request,
        "community/feed/post_list.html",
        {
            "posts": qs,
            "post_types": BasePost.PostType.choices,
            "selected_type": selected_type,
            "selected_tag": selected_tag,
            "q": q,
            "top_tags": top_tags,
        },
    )



@login_required
def post_create_view(request):
    if request.method == "POST":
        # anti-spam cooldown: 1 post per 30s
        key = f"cooldown_post_{request.user.id}"
        if cache.get(key):
            messages.error(request, "Slow down — please wait a bit before creating another post.")
            return redirect("feed:post_create")
        cache.set(key, True, 30)

        form = BasePostForm(request.POST)
        images = request.FILES.getlist("images")

        if len(images) > 5:
            form.add_error(None, "You can upload a maximum of 5 images per post.")
        for f in images:
            ctype = getattr(f, "content_type", "")
            if not ctype.startswith("image/"):
                form.add_error(None, f"File '{f.name}' is not an image.")

        if form.is_valid():
            with transaction.atomic():
                base_post = form.save(commit=False)
                base_post.author = request.user
                base_post.save()

                # Tags
                tag_names = form.cleaned_data.get("tags", [])
                tags = []
                for name in tag_names:
                    t, _ = Tag.objects.get_or_create(name=name)
                    tags.append(t)
                if tags:
                    base_post.tags.set(tags)


                model_cls = TYPE_MODEL_MAP.get(base_post.post_type)
                model_cls.objects.create(post=base_post)

                for f in images:
                    PostImage.objects.create(post=base_post, image=f)

            messages.success(request, "Post created successfully.")
            return redirect("feed:post_detail", post_id=base_post.id)
    else:
        form = BasePostForm()

    return render(request, "community/feed/post_create.html", {"form": form})


def post_detail_view(request, post_id: int):
    post = get_object_or_404(BasePost, id=post_id)
    if post.is_hidden and not is_moderator(request.user):
        return redirect("feed:post_list")

    images = post.images.all().order_by("id")
    comments = post.comments.filter(is_hidden=False).order_by("created_at")

    liked = False
    if request.user.is_authenticated:
        liked = PostLike.objects.filter(post=post, user=request.user).exists()

    comment_form = CommentForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("/login/")

        # anti-spam cooldown: 1 comment per 10s
        key = f"cooldown_comment_{request.user.id}"
        if cache.get(key):
            messages.error(request, "Please wait a few seconds before commenting again.")
            return redirect("feed:post_detail", post_id=post.id)
        cache.set(key, True, 10)

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            Comment.objects.create(
                post=post,
                author=request.user,
                text=comment_form.cleaned_data["text"],
            )
            return redirect("feed:post_detail", post_id=post.id)

    context = {
        "post": post,
        "images": images,
        "comments": comments,
        "comment_form": comment_form,
        "liked": liked,
        "like_count": PostLike.objects.filter(post=post).count(),
        "comment_count": comments.count(),
        "can_manage_post": _owner_or_mod_required(request.user, post.author_id),
        "is_moderator": is_moderator(request.user),
    }
    return render(request, "community/feed/post_detail.html", context)


@login_required
@require_POST
def post_like_toggle_view(request, post_id: int):
    post = get_object_or_404(BasePost, id=post_id, is_hidden=False)

    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/feed/"
    return redirect(next_url)


# ---------- Edit / Delete (P2) ----------

@login_required
def post_edit_view(request, post_id: int):
    post = get_object_or_404(BasePost, id=post_id)
    if not _owner_or_mod_required(request.user, post.author_id):
        return HttpResponseForbidden("Not allowed.")

    if request.method == "POST":
        form = BasePostForm(request.POST, instance=post)
        # prevent changing type after creation (keeps separate-type table consistent)
        form.fields["post_type"].disabled = True

        if form.is_valid():
            post = form.save()
        
            tag_names = form.cleaned_data.get("tags", [])
            tags = []
            for name in tag_names:
                t, _ = Tag.objects.get_or_create(name=name)
                tags.append(t)
            post.tags.set(tags)

            messages.success(request, "Post updated.")
            return redirect("feed:post_detail", post_id=post.id)

    else:

        form = BasePostForm(instance=post)

        form.initial["tags"] = ", ".join(post.tags.values_list("name", flat=True))

        form.fields["post_type"].disabled = True

    return render(request, "community//feed/post_edit.html", {"form": form, "post": post})


@login_required
@require_POST
def post_delete_view(request, post_id: int):
    post = get_object_or_404(BasePost, id=post_id)
    if not _owner_or_mod_required(request.user, post.author_id):
        return HttpResponseForbidden("Not allowed.")
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("feed:post_list")


@login_required
@require_POST
def comment_delete_view(request, comment_id: int):
    c = get_object_or_404(Comment, id=comment_id)
    if not _owner_or_mod_required(request.user, c.author_id):
        return HttpResponseForbidden("Not allowed.")
    post_id = c.post_id
    c.delete()
    messages.success(request, "Comment deleted.")
    return redirect("feed:post_detail", post_id=post_id)


# ---------- Reporting (User) ----------

@login_required
def report_post_view(request, post_id: int):
    post = get_object_or_404(BasePost, id=post_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.reporter = request.user
            r.content_type = ContentType.objects.get_for_model(BasePost)
            r.object_id = post.id
            r.save()
            messages.success(request, "Reported. Thanks for keeping the community safe.")
            return redirect("feed:post_detail", post_id=post.id)
    else:
        form = ReportForm()

    return render(request, "community/feed/report.html", {"form": form, "target_label": f"Post: {post.title}"})


@login_required
def report_comment_view(request, comment_id: int):
    c = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.reporter = request.user
            r.content_type = ContentType.objects.get_for_model(Comment)
            r.object_id = c.id
            r.save()
            messages.success(request, "Reported. Thanks for keeping the community safe.")
            return redirect("feed:post_detail", post_id=c.post_id)
    else:
        form = ReportForm()

    return render(request, "community/feed/report.html", {"form": form, "target_label": "Comment"})


# ---------- Moderation: Reports queue + actions ----------

@moderator_required
def mod_reports_view(request):
    open_reports = Report.objects.filter(status="OPEN").order_by("-created_at")
    return render(request, "community/feed/mod_reports.html", {"reports": open_reports})


@moderator_required
@require_POST
def mod_report_action_view(request, report_id: int):
    report = get_object_or_404(Report, id=report_id)
    action = request.POST.get("action", "")

    target = report.target  # can be None if deleted
    if action in ("hide", "unhide") and target is not None:
        if hasattr(target, "is_hidden"):
            target.is_hidden = (action == "hide")
            target.save(update_fields=["is_hidden"])
            messages.success(request, f"Target {action}d.")
        else:
            messages.error(request, "Target cannot be hidden.")
        return redirect("feed:mod_reports")

    if action == "delete" and target is not None:
        target.delete()
        messages.success(request, "Target deleted.")
        return redirect("feed:mod_reports")

    if action == "resolve":
        report.status = "RESOLVED"
        report.save(update_fields=["status"])
        messages.success(request, "Report resolved.")
        return redirect("feed:mod_reports")

    if action == "ignore":
        report.status = "IGNORED"
        report.save(update_fields=["status"])
        messages.success(request, "Report ignored.")
        return redirect("feed:mod_reports")

    messages.error(request, "Invalid action.")
    return redirect("feed:mod_reports")
