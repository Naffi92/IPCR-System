from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def role_required(*role_names):
    """
    Restrict a view to users who belong to at least one of the given roles.
    Superusers always pass.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            user_groups = set(request.user.groups.values_list('name', flat=True))
            if user_groups & set(role_names):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped
    return decorator