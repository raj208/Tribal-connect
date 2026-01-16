from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_moderator_group(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    from feed.models import BasePost, Comment, Report
    from calendar_app.models import CulturalEvent   # <-- FIXED (was calendar_app)
    from opportunities.models import Opportunity

    group, _ = Group.objects.get_or_create(name="Moderator")

    managed_models = [BasePost, Comment, Report, CulturalEvent, Opportunity]

    wanted_codenames = []
    for model in managed_models:
        mn = model._meta.model_name
        wanted_codenames += [f"view_{mn}", f"change_{mn}", f"delete_{mn}"]
        if model in (CulturalEvent, Opportunity):
            wanted_codenames.append(f"add_{mn}")

    perms_to_set = []
    for model in managed_models:
        ct = ContentType.objects.get_for_model(model)
        perms_to_set += list(Permission.objects.filter(content_type=ct, codename__in=wanted_codenames))

    perms_to_set = list({p.id: p for p in perms_to_set}.values())
    group.permissions.set(perms_to_set)


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from . import signals  # noqa
        post_migrate.connect(create_moderator_group, sender=self)
