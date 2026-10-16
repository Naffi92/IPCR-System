def user_roles(request):
    """Make the current user's role names available in every template."""
    if request.user.is_authenticated:
        return {
            'user_groups': list(
                request.user.groups.values_list('name', flat=True)
            )
        }
    return {'user_groups': []}