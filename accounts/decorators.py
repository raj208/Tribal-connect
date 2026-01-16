from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .utils import is_moderator


def moderator_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_moderator(request.user):
            return HttpResponseForbidden("Moderator access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped
