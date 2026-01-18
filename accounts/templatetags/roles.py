from django import template

register = template.Library()

@register.filter(name="is_moderator_user")
def is_moderator_user(user):
    return user.is_authenticated and user.groups.filter(name="Moderator").exists()

@register.filter(name="is_artisan_user")
def is_artisan_user(user):
    return user.is_authenticated and getattr(user, "role", None) == "ARTISAN"

@register.filter(name="is_customer_user")
def is_customer_user(user):
    return user.is_authenticated and getattr(user, "role", None) == "CUSTOMER"
