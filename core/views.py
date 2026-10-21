from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .models import RatingPeriod, Division, Employee, IPCR
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import IPCRTargetForm
from .models import RatingPeriod, Division, Employee, IPCR, IPCRTarget
from .forms import IPCRTargetForm, AppraisalFormSet
from .forms import IPCRTargetForm, AppraisalFormSet, BehavioralRatingFormSet, CriticalIncidentForm
from .models import RatingPeriod, Division, Employee, IPCR, IPCRTarget, BehavioralDimension, BehavioralRating, CriticalIncident

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

@login_required
def submit_ipcr(request):
    """Ratee view: submit the draft IPCR for approval."""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('core:home')

    active_period = RatingPeriod.objects.filter(is_active=True).first()
    if not active_period:
        return redirect('core:my_ipcr')

    ipcr = get_object_or_404(IPCR, rating_period=active_period, employee=employee)

    if request.method == 'POST':
        # Validation: Cannot submit if total weight != 100
        total_weight = sum(t.weight for t in ipcr.targets.all())
        if total_weight != 100:
            messages.error(request, f"Cannot submit. Total weight is {total_weight}%. It must be exactly 100%.")
            return redirect('core:my_ipcr')
        
        if not ipcr.targets.exists():
            messages.error(request, "Cannot submit. You have no targets.")
            return redirect('core:my_ipcr')

        # Validation: Must have a supervisor assigned
        if not employee.supervisor:
            messages.error(request, "Cannot submit. You do not have a supervisor assigned. Please contact HRMO.")
            return redirect('core:my_ipcr')

        # Perform submission
        ipcr.status = 'submitted'
        ipcr.main_appraiser = employee.supervisor
        from django.utils import timezone
        ipcr.submitted_at = timezone.now()
        ipcr.save()
        
        messages.success(request, "IPCR submitted successfully to your supervisor.")
        return redirect('core:my_ipcr')

    return redirect('core:my_ipcr')


@role_required('Rater', 'Division Head')
def supervisor_dashboard(request):
    """Rater view: list of subordinates' IPCRs pending review."""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your account is not linked to an Employee profile.")
        return redirect('core:home')

    active_period = RatingPeriod.objects.filter(is_active=True).first()
    
    # Get subordinates
    subordinates = Employee.objects.filter(supervisor=employee)
    
    # Get their IPCRs for the active period
    ipcrs = IPCR.objects.filter(
        rating_period=active_period,
        employee__in=subordinates
    ).order_by('status', 'employee__user__last_name')

    context = {
        'active_period': active_period,
        'ipcrs': ipcrs,
    }
    return render(request, 'core/supervisor_dashboard.html', context)


@role_required('Rater', 'Division Head')
def review_ipcr(request, ipcr_id):
    """Rater view: review an IPCR and approve/return it."""
    try:
        supervisor = request.user.employee
    except Employee.DoesNotExist:
        return redirect('core:home')

    ipcr = get_object_or_404(IPCR, id=ipcr_id, main_appraiser=supervisor)
    targets = ipcr.targets.all()
    total_weight = sum(t.weight for t in targets)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            ipcr.status = 'approved'
            from django.utils import timezone
            ipcr.approved_at = timezone.now()
            ipcr.save()
            messages.success(request, f"IPCR for {ipcr.employee.user.get_full_name() or ipcr.employee.user.username} has been approved.")
        
        elif action == 'return':
            ipcr.status = 'returned'
            ipcr.save()
            messages.warning(request, f"IPCR returned to {ipcr.employee.user.get_full_name() or ipcr.employee.user.username} for revision.")
            
        return redirect('core:supervisor_dashboard')

    context = {
        'ipcr': ipcr,
        'targets': targets,
        'total_weight': total_weight,
    }
    return render(request, 'core/review_ipcr.html', context)

@role_required('Rater', 'Division Head')
def appraise_ipcr(request, ipcr_id):
    """Rater view: input actuals, 1-5 Q/E/T ratings, and BDF ratings."""
    try:
        supervisor = request.user.employee
    except Employee.DoesNotExist:
        return redirect('core:home')

    ipcr = get_object_or_404(IPCR, id=ipcr_id, main_appraiser=supervisor)
    
    if ipcr.status not in ['approved', 'appraised']:
        messages.error(request, "You can only appraise an IPCR that has been approved.")
        return redirect('core:supervisor_dashboard')

    # Ensure BehavioralRating objects exist for all active dimensions
    active_dimensions = BehavioralDimension.objects.filter(is_active=True)
    for dim in active_dimensions:
        BehavioralRating.objects.get_or_create(ipcr=ipcr, dimension=dim)

    if request.method == 'POST':
        target_formset = AppraisalFormSet(request.POST, queryset=ipcr.targets.all())
        bdf_formset = BehavioralRatingFormSet(request.POST, queryset=ipcr.behavioral_ratings.all())
        
        if target_formset.is_valid() and bdf_formset.is_valid():
            target_formset.save()
            bdf_formset.save()
            
            ipcr.status = 'appraised'
            ipcr.save()
            messages.success(request, "Appraisal and BDF saved successfully.")
            return redirect('core:supervisor_dashboard')
    else:
        target_formset = AppraisalFormSet(queryset=ipcr.targets.all())
        bdf_formset = BehavioralRatingFormSet(queryset=ipcr.behavioral_ratings.all())

    context = {
        'ipcr': ipcr,
        'formset': target_formset,
        'bdf_formset': bdf_formset,
    }
    return render(request, 'core/appraise_ipcr.html', context)