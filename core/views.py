from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Temporary home page — will become the role-based dashboard."""
    return render(request, 'core/home.html')