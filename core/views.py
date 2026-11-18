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
    """Ratee view: Create/View their IPCR."""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your account is not linked to an Employee profile.")
        return redirect('core:home')

    # Find active rating period
    active_period = RatingPeriod.objects.filter(is_active=True).first()
    if not active_period:
        messages.warning(request, "There is no active rating period.")
        return render(request, 'core/ipcr_unavailable.html')

    # Check if we are in the Target Phase
    today = timezone.now().date()
    is_target_phase = active_period.target_start <= today <= active_period.target_end
    is_accomplishment_phase = active_period.accomplishment_start <= today <= active_period.accomplishment_end

    # Get or Create IPCR for this user and period
    # For now, we default to the Faculty template if they are Faculty, else Staff
    template_type = employee.position.type if employee.position else 'Staff'
    default_template = Template.objects.filter(evaluation_type=template_type).first()

    ipcr, created = IPCR.objects.get_or_create(
        employee=employee,
        rating_period=active_period,
        defaults={'template': default_template, 'status': 'Draft'}
    )

    # Get existing rows
    rows = ipcr.rows.all()

    context = {
        'ipcr': ipcr,
        'active_period': active_period,
        'is_target_phase': is_target_phase,
        'is_accomplishment_phase': is_accomplishment_phase,
        'rows': rows,
        'template': ipcr.template,
    }
    return render(request, 'core/my_ipcr.html', context)