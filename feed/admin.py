from django.contrib import admin
from .models import (
    BasePost, FolktalePost, FestivalPost, EducationPost, OralHighlightPost, AnnouncementPost,
    PostImage, Comment, PostLike, Report
)

from .models import Tag

admin.site.register(BasePost)
admin.site.register(FolktalePost)
admin.site.register(FestivalPost)
admin.site.register(EducationPost)
admin.site.register(OralHighlightPost)
admin.site.register(AnnouncementPost)
admin.site.register(PostImage)
admin.site.register(Comment)
admin.site.register(PostLike)
admin.site.register(Report)

admin.site.register(Tag)

