from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self) -> str:
        return self.name


class BasePost(models.Model):
    class PostType(models.TextChoices):
        FOLKTALE = "FOLKTALE", "Folktale"
        FESTIVAL = "FESTIVAL", "Festival"
        EDUCATION = "EDUCATION", "Education"
        ORAL = "ORAL", "Oral Highlight"
        ANNOUNCEMENT = "ANNOUNCEMENT", "Announcement"


    tags = models.ManyToManyField("feed.Tag", blank=True, related_name="posts")


    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    post_type = models.CharField(max_length=20, choices=PostType.choices)

    title = models.CharField(max_length=200)
    body = models.TextField()

    is_hidden = models.BooleanField(default=False)  # for moderation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Likes
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, through="PostLike", related_name="liked_posts", blank=True)

    def __str__(self) -> str:
        return f"{self.post_type} | {self.title}"


# --- Separate Types (as requested) ---
# These are 1-1 linked "type tables". No extra fields now, but you can add later easily.

class FolktalePost(models.Model):
    post = models.OneToOneField(BasePost, on_delete=models.CASCADE, related_name="folktale")

    def save(self, *args, **kwargs):
        if self.post.post_type != BasePost.PostType.FOLKTALE:
            self.post.post_type = BasePost.PostType.FOLKTALE
            self.post.save(update_fields=["post_type"])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Folktale({self.post_id})"


class FestivalPost(models.Model):
    post = models.OneToOneField(BasePost, on_delete=models.CASCADE, related_name="festival")

    def save(self, *args, **kwargs):
        if self.post.post_type != BasePost.PostType.FESTIVAL:
            self.post.post_type = BasePost.PostType.FESTIVAL
            self.post.save(update_fields=["post_type"])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Festival({self.post_id})"


class EducationPost(models.Model):
    post = models.OneToOneField(BasePost, on_delete=models.CASCADE, related_name="education")

    def save(self, *args, **kwargs):
        if self.post.post_type != BasePost.PostType.EDUCATION:
            self.post.post_type = BasePost.PostType.EDUCATION
            self.post.save(update_fields=["post_type"])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Education({self.post_id})"


class OralHighlightPost(models.Model):
    post = models.OneToOneField(BasePost, on_delete=models.CASCADE, related_name="oral")

    def save(self, *args, **kwargs):
        if self.post.post_type != BasePost.PostType.ORAL:
            self.post.post_type = BasePost.PostType.ORAL
            self.post.save(update_fields=["post_type"])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Oral({self.post_id})"


class AnnouncementPost(models.Model):
    post = models.OneToOneField(BasePost, on_delete=models.CASCADE, related_name="announcement")

    def save(self, *args, **kwargs):
        if self.post.post_type != BasePost.PostType.ANNOUNCEMENT:
            self.post.post_type = BasePost.PostType.ANNOUNCEMENT
            self.post.save(update_fields=["post_type"])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Announcement({self.post_id})"


class PostImage(models.Model):
    post = models.ForeignKey(BasePost, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/%Y/%m/%d/")
    caption = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image({self.id}) for Post({self.post_id})"


class Comment(models.Model):
    post = models.ForeignKey(BasePost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()

    is_hidden = models.BooleanField(default=False)  # moderation
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment({self.id}) on Post({self.post_id})"


class PostLike(models.Model):
    post = models.ForeignKey(BasePost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_like_per_user_per_post")
        ]

    def __str__(self) -> str:
        return f"Like(Post={self.post_id}, User={self.user_id})"


class Report(models.Model):
    """
    Generic report for Post / Comment / Opportunity etc.
    We'll start with Post & Comment and extend easily.
    """
    class Reason(models.TextChoices):
        SPAM = "SPAM", "Spam"
        ABUSE = "ABUSE", "Abusive content"
        MISINFO = "MISINFO", "Misinformation"
        OTHER = "OTHER", "Other"

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=20, choices=Reason.choices, default=Reason.OTHER)
    note = models.TextField(blank=True)

    # Generic target
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")

    status = models.CharField(
        max_length=20,
        choices=[("OPEN", "Open"), ("RESOLVED", "Resolved"), ("IGNORED", "Ignored")],
        default="OPEN",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Report({self.id}) {self.reason} {self.status}"
