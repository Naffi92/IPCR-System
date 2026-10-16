from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .models import RatingPeriod, Division, Employee, IPCR


@login_required
def home(request):
    """Temporary home page — will become role-aware later."""
    return render(request, 'core/home.html')


@role_required('HRMO')
def dashboard(request):
    """
    HRMO Submission Monitoring Dashboard.
    Shows compliance stats per division for the active rating period.
    """
    active_period = RatingPeriod.objects.filter(is_active=True).first()

    division_stats = []
    totals = {
        'employees': 0,
        'submitted': 0,
        'approved': 0,
        'returned': 0,
        'draft': 0,
        'no_ipcr': 0,
    }

    if active_period:
        for division in Division.objects.all().order_by('name'):
            employees = Employee.objects.filter(division=division)
            total = employees.count()

            ipcrs = IPCR.objects.filter(
                rating_period=active_period,
                employee__division=division,
            )

            submitted = ipcrs.filter(status='submitted').count()
            approved = ipcrs.filter(status='approved').count()
            returned = ipcrs.filter(status='returned').count()
            draft = ipcrs.filter(status='draft').count()
            with_ipcr = ipcrs.count()
            no_ipcr = max(total - with_ipcr, 0)

            compliance = ((submitted + approved) / total * 100) if total else 0

            division_stats.append({
                'division': division,
                'total': total,
                'submitted': submitted,
                'approved': approved,
                'returned': returned,
                'draft': draft,
                'no_ipcr': no_ipcr,
                'compliance_rate': round(compliance, 1),
            })

            totals['employees'] += total
            totals['submitted'] += submitted
            totals['approved'] += approved
            totals['returned'] += returned
            totals['draft'] += draft
            totals['no_ipcr'] += no_ipcr

    overall_compliance = (
        ((totals['submitted'] + totals['approved']) / totals['employees'] * 100)
        if totals['employees'] else 0
    )

    context = {
        'active_period': active_period,
        'division_stats': division_stats,
        'totals': totals,
        'overall_compliance': round(overall_compliance, 1),
    }
    return render(request, 'core/dashboard.html', context)