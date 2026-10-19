from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .models import RatingPeriod, Division, Employee, IPCR
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import IPCRTargetForm
from .models import RatingPeriod, Division, Employee, IPCR, IPCRTarget

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

@login_required
def my_ipcr(request):
    """Ratee view: list targets for the active rating period."""
    active_period = RatingPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.warning(request, "There is no active rating period. Please contact HRMO.")
        return redirect('core:home')
        
    # Check if user has an Employee profile
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your account is not linked to an Employee profile. Please contact HRMO.")
        return redirect('core:home')

    # Get or create the IPCR for this employee and period
    ipcr, created = IPCR.objects.get_or_create(
        rating_period=active_period,
        employee=employee,
        defaults={'status': 'draft'}
    )
    
    targets = ipcr.targets.all()
    total_weight = sum(t.weight for t in targets)
    
    context = {
        'ipcr': ipcr,
        'targets': targets,
        'total_weight': total_weight,
        'active_period': active_period,
    }
    return render(request, 'core/my_ipcr.html', context)


@login_required
def add_target(request):
    """Ratee view: add a new target to their IPCR."""
    active_period = RatingPeriod.objects.filter(is_active=True).first()
    if not active_period:
        return redirect('core:my_ipcr')

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('core:home')

    ipcr, _ = IPCR.objects.get_or_create(
        rating_period=active_period, employee=employee, defaults={'status': 'draft'}
    )

    if ipcr.status != 'draft':
        messages.error(request, "Cannot add targets. IPCR is already submitted or approved.")
        return redirect('core:my_ipcr')

    if request.method == 'POST':
        form = IPCRTargetForm(request.POST, division=employee.division)
        if form.is_valid():
            target = form.save(commit=False)
            target.ipcr = ipcr
            target.save()
            messages.success(request, "Target added successfully.")
            return redirect('core:my_ipcr')
    else:
        form = IPCRTargetForm(division=employee.division)

    return render(request, 'core/target_form.html', {'form': form, 'title': 'Add Target'})


@login_required
def edit_target(request, target_id):
    """Ratee view: edit an existing target."""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('core:home')

    target = get_object_or_404(IPCRTarget, id=target_id, ipcr__employee=employee)
    
    if target.ipcr.status != 'draft':
        messages.error(request, "Cannot edit targets. IPCR is already submitted or approved.")
        return redirect('core:my_ipcr')

    if request.method == 'POST':
        form = IPCRTargetForm(request.POST, instance=target, division=employee.division)
        if form.is_valid():
            form.save()
            messages.success(request, "Target updated successfully.")
            return redirect('core:my_ipcr')
    else:
        form = IPCRTargetForm(instance=target, division=employee.division)

    return render(request, 'core/target_form.html', {'form': form, 'title': 'Edit Target'})


@login_required
def delete_target(request, target_id):
    """Ratee view: delete an existing target."""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('core:home')

    target = get_object_or_404(IPCRTarget, id=target_id, ipcr__employee=employee)
    
    if target.ipcr.status != 'draft':
        messages.error(request, "Cannot delete targets. IPCR is already submitted or approved.")
        return redirect('core:my_ipcr')

    if request.method == 'POST':
        target.delete()
        messages.success(request, "Target deleted.")
        return redirect('core:my_ipcr')

    return render(request, 'core/target_confirm_delete.html', {'target': target})