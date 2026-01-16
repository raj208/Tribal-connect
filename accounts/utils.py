def is_moderator(user) -> bool:
    """
    True if user is authenticated and is in Moderator group OR is staff/superuser.
    """
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or user.groups.filter(name="Moderator").exists()


def is_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff
