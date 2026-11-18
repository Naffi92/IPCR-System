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