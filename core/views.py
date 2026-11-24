from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from .models import (
    Template, TemplateCategory, TemplateGoal, TemplateKRA, TemplateColumn
)
from .forms import (
    TemplateForm, TemplateCategoryForm, TemplateGoalForm, TemplateKRAForm, TemplateColumnForm
)
from .forms import RatingPeriodForm, PositionCategoryWeightForm
from .models import RatingPeriod, PositionCategoryWeight, Position
from django.utils import timezone
from .models import IPCR, IPCRRow
from .models import (
    Template, TemplateCategory, TemplateGoal, TemplateKRA, TemplateColumn,
    RatingPeriod, PositionCategoryWeight, Position, IPCR, IPCRRow, Employee
)
from django.core.exceptions import ObjectDoesNotExist

from .forms import TemplateSelectionForm, TemplateColumnForm
from .models import IPCRRow
from .forms import (
    TemplateForm, TemplateCategoryForm, TemplateGoalForm, TemplateKRAForm, 
    TemplateColumnForm, TemplateColumnEditForm, TemplateSelectionForm, RatingPeriodForm
)

# --- HOME & DASHBOARD ---
@login_required
def home(request):
    return render(request, 'core/home.html')

@role_required('HRMO')
def template_dashboard(request):
    templates = Template.objects.all()
    return render(request, 'core/template_dashboard.html', {'templates': templates})

@role_required('HRMO')
def create_template(request):
    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Template created successfully.")
            return redirect('core:template_dashboard')
    else:
        form = TemplateForm()
    return render(request, 'core/template_form.html', {'form': form, 'title': 'Create Template'})

@role_required('HRMO')
def template_detail(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    categories = template.categories.all().order_by('order')
    columns = template.columns.all().order_by('order')
    
    # Calculate remaining weight
    total_weight = sum(cat.default_weight for cat in categories)
    remaining_weight = 100 - total_weight
    
    context = {
        'template': template,
        'categories': categories,
        'columns': columns,
        'category_form': TemplateCategoryForm(),
        'column_form': TemplateColumnForm(),
        'total_weight': total_weight,
        'remaining_weight': remaining_weight,
    }
    return render(request, 'core/template_detail.html', context)

# --- CATEGORY VIEWS ---
@role_required('HRMO')
def add_category(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        form = TemplateCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.template = template
            category.save()
            messages.success(request, "Category added.")
    return redirect('core:template_detail', template_id=template.id)

@role_required('HRMO')
def delete_category(request, category_id):
    category = get_object_or_404(TemplateCategory, id=category_id)
    template_id = category.template.id
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect('core:template_detail', template_id=template_id)

# --- GOAL VIEWS ---
@role_required('HRMO')
def add_goal(request, category_id):
    category = get_object_or_404(TemplateCategory, id=category_id)
    if request.method == 'POST':
        form = TemplateGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.category = category
            goal.save()
            messages.success(request, "Goal added.")
    return redirect('core:template_detail', template_id=category.template.id)

@role_required('HRMO')
def delete_goal(request, goal_id):
    goal = get_object_or_404(TemplateGoal, id=goal_id)
    template_id = goal.category.template.id
    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Goal deleted.")
    return redirect('core:template_detail', template_id=template_id)

# --- KRA VIEWS ---
@role_required('HRMO')
def add_kra(request, goal_id):
    goal = get_object_or_404(TemplateGoal, id=goal_id)
    if request.method == 'POST':
        form = TemplateKRAForm(request.POST)
        if form.is_valid():
            kra = form.save(commit=False)
            kra.goal = goal
            kra.save()
            messages.success(request, "KRA added.")
    return redirect('core:template_detail', template_id=goal.category.template.id)

@role_required('HRMO')
def delete_kra(request, kra_id):
    kra = get_object_or_404(TemplateKRA, id=kra_id)
    template_id = kra.goal.category.template.id
    if request.method == 'POST':
        kra.delete()
        messages.success(request, "KRA deleted.")
    return redirect('core:template_detail', template_id=template_id)

# --- COLUMN VIEWS ---
@role_required('HRMO')
def add_column(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        form = TemplateColumnForm(request.POST)
        if form.is_valid():
            column = form.save(commit=False)
            column.template = template
            column.save()
            messages.success(request, "Column added.")
    return redirect('core:template_detail', template_id=template.id)

@role_required('HRMO')
def edit_column(request, column_id):
    column = get_object_or_404(TemplateColumn, id=column_id)
    if request.method == 'POST':
        form = TemplateColumnEditForm(request.POST, instance=column)
        if form.is_valid():
            form.save()
            messages.success(request, "Column updated.")
            return redirect('core:template_detail', template_id=column.template.id)
    else:
        form = TemplateColumnEditForm(instance=column)
    return render(request, 'core/simple_form.html', {'form': form, 'title': 'Edit Column', 'cancel_url': column.template.id})

@role_required('HRMO')
def delete_column(request, column_id):
    column = get_object_or_404(TemplateColumn, id=column_id)
    template_id = column.template.id
    if request.method == 'POST':
        column.delete()
        messages.success(request, "Column deleted.")
    return redirect('core:template_detail', template_id=template_id)

# --- RATING PERIOD VIEWS ---
@role_required('HRMO')
def rating_period_dashboard(request):
    periods = RatingPeriod.objects.all().order_by('-target_start')
    return render(request, 'core/rating_period_dashboard.html', {'periods': periods})

@role_required('HRMO')
def create_rating_period(request):
    if request.method == 'POST':
        form = RatingPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rating Period created successfully.")
            return redirect('core:rating_period_dashboard')
    else:
        form = RatingPeriodForm()
    return render(request, 'core/rating_period_form.html', {'form': form, 'title': 'Create Rating Period'})

# --- POSITION MATRIX VIEWS ---
@role_required('HRMO')
def position_matrix(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    # Get all Faculty positions
    positions = Position.objects.filter(type='Faculty')
    categories = template.categories.all()
    
    # We will handle the matrix data in the template using a custom loop
    matrix_data = []
    for pos in positions:
        pos_weights = {}
        for cat in categories:
            weight = PositionCategoryWeight.objects.filter(position=pos, category=cat).first()
            pos_weights[cat.id] = weight.weight_percentage if weight else cat.default_weight
        matrix_data.append({'position': pos, 'weights': pos_weights})
        
    if request.method == 'POST':
        # Save the matrix safely
        for pos in positions:
            for cat in categories:
                field_name = f"weight_{pos.id}_{cat.id}"
                val = request.POST.get(field_name)
                
                # If the user entered a value, convert to float, else default to 0.00
                weight_val = float(val) if val else 0.00
                
                # update_or_create prevents the IntegrityError
                PositionCategoryWeight.objects.update_or_create(
                    position=pos, 
                    category=cat,
                    defaults={'weight_percentage': weight_val}
                )
        messages.success(request, "Position Matrix updated.")
        return redirect('core:template_dashboard')

    context = {
        'template': template,
        'categories': categories,
        'matrix_data': matrix_data,
    }
    return render(request, 'core/position_matrix.html', context)

@login_required
def my_ipcr(request):
    try:
        employee = request.user.employee
    except ObjectDoesNotExist:
        messages.error(request, "Your account is not linked to an Employee profile.")
        return redirect('core:home')

    # Get ALL active rating periods, not just the first one
    active_periods = RatingPeriod.objects.filter(is_active=True).order_by('-target_start')
    
    if not active_periods.exists():
        messages.warning(request, "There is no active rating period.")
        return render(request, 'core/ipcr_unavailable.html')

    # Handle period selection via GET or POST
    selected_period_id = request.POST.get('rating_period') or request.GET.get('period')
    if selected_period_id:
        active_period = active_periods.filter(id=selected_period_id).first()
    else:
        active_period = active_periods.first() # Default to the most recent

    today = timezone.now().date()
    is_target_phase = active_period.target_start <= today <= active_period.target_end
    is_accomplishment_phase = active_period.accomplishment_start <= today <= active_period.accomplishment_end

    ipcr, created = IPCR.objects.get_or_create(
        employee=employee,
        rating_period=active_period,
        defaults={'status': 'Draft'}
    )

    template_form = None
    if not ipcr.template:
        user_type = employee.position.type if employee.position else 'Staff'
        if request.method == 'POST' and 'select_template' in request.POST:
            template_form = TemplateSelectionForm(request.POST, user_type=user_type)
            if template_form.is_valid():
                ipcr.template = template_form.cleaned_data['template']
                ipcr.save()
                messages.success(request, "Template selected successfully.")
                return redirect(f"{request.path}?period={active_period.id}")
        else:
            template_form = TemplateSelectionForm(user_type=user_type)

    rows = ipcr.rows.all().order_by('kra__goal__category__order', 'kra__goal__order', 'kra__order')
    
    context = {
        'ipcr': ipcr,
        'active_period': active_period,
        'active_periods': active_periods, # Pass all active periods
        'is_target_phase': is_target_phase,
        'is_accomplishment_phase': is_accomplishment_phase,
        'template_form': template_form,
        'rows': rows,
    }
    return render(request, 'core/my_ipcr.html', context)


@login_required
def add_ipcr_row(request):
    try:
        employee = request.user.employee
    except ObjectDoesNotExist:
        return redirect('core:home')

    active_period = RatingPeriod.objects.filter(is_active=True).first()
    
    # THIS IS THE MISSING LINE THAT CAUSED THE ERROR
    ipcr = get_object_or_404(IPCR, employee=employee, rating_period=active_period)

    if not ipcr.template:
        messages.error(request, "Please select a Template first.")
        return redirect('core:my_ipcr')

    all_columns = ipcr.template.columns.all().order_by('order')

    if request.method == 'POST':
        kra_id = request.POST.get('kra_id')
        if not kra_id:
            messages.error(request, "You must select a KRA.")
            return redirect('core:add_ipcr_row')
            
        kra = get_object_or_404(TemplateKRA, id=kra_id)
        
        dynamic_data = {}
        for col in all_columns:
            val = request.POST.get(f'col_{col.id}')
            if val:
                dynamic_data[col.name] = val
                
        IPCRRow.objects.create(ipcr=ipcr, kra=kra, dynamic_data=dynamic_data)
        messages.success(request, "Target added successfully.")
        return redirect('core:my_ipcr')

    categories = ipcr.template.categories.all().prefetch_related('goals__kras')

    context = {
        'ipcr': ipcr,
        'categories': categories,
        'all_columns': all_columns,
    }
    return render(request, 'core/add_ipcr_row.html', context)

@role_required('HRMO')
def edit_rating_period(request, period_id):
    period = get_object_or_404(RatingPeriod, id=period_id)
    if request.method == 'POST':
        form = RatingPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, "Rating Period updated.")
            return redirect('core:rating_period_dashboard')
    else:
        form = RatingPeriodForm(instance=period)
    return render(request, 'core/rating_period_form.html', {'form': form, 'title': 'Edit Rating Period'})

@role_required('HRMO')
def delete_rating_period(request, period_id):
    period = get_object_or_404(RatingPeriod, id=period_id)
    if request.method == 'POST':
        period.delete()
        messages.success(request, "Rating Period deleted.")
    return redirect('core:rating_period_dashboard')

@role_required('HRMO')
def edit_template(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, "Template updated.")
            return redirect('core:template_dashboard')
    else:
        form = TemplateForm(instance=template)
    return render(request, 'core/template_form.html', {'form': form, 'title': 'Edit Template'})

@role_required('HRMO')
def delete_template(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        template.delete()
        messages.success(request, "Template deleted.")
    return redirect('core:template_dashboard')

@login_required
def submit_target(request, ipcr_id):
    """Ratee submits their targets to the Rater."""
    ipcr = get_object_or_404(IPCR, id=ipcr_id, employee=request.user.employee)
    
    if not ipcr.rows.exists():
        messages.error(request, "You cannot submit an empty IPCR.")
        return redirect('core:my_ipcr')
        
    ipcr.status = 'Target Submitted'
    ipcr.save()
    messages.success(request, "Your targets have been submitted to your supervisor.")
    return redirect('core:my_ipcr')

@login_required
def delete_ipcr_row(request, row_id):
    row = get_object_or_404(IPCRRow, id=row_id, ipcr__employee=request.user.employee)
    if row.ipcr.status not in ['Draft', 'Returned']:
        messages.error(request, "You cannot delete targets after submission.")
    else:
        if request.method == 'POST':
            row.delete()
            messages.success(request, "Target deleted.")
    return redirect('core:my_ipcr')