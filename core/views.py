from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from .models import Template, TemplateCategory, TemplateKRA, TemplateColumn
from .forms import TemplateForm, TemplateCategoryForm, TemplateKRAForm, TemplateColumnForm

@login_required
def home(request):
    return render(request, 'core/home.html')

@role_required('HRMO')
def template_dashboard(request):
    """Lists all available Templates."""
    templates = Template.objects.all()
    return render(request, 'core/template_dashboard.html', {'templates': templates})

@role_required('HRMO')
def create_template(request):
    """Create a new Template."""
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
    """View a specific Template, showing its Categories, KRAs, and Columns."""
    template = get_object_or_404(Template, id=template_id)
    categories = template.categories.all().order_by('order')
    columns = template.columns.all().order_by('order')
    
    context = {
        'template': template,
        'categories': categories,
        'columns': columns,
        'category_form': TemplateCategoryForm(),
        'column_form': TemplateColumnForm(),
    }
    return render(request, 'core/template_detail.html', context)

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
def add_kra(request, category_id):
    category = get_object_or_404(TemplateCategory, id=category_id)
    if request.method == 'POST':
        form = TemplateKRAForm(request.POST)
        if form.is_valid():
            kra = form.save(commit=False)
            kra.category = category
            kra.save()
            messages.success(request, "KRA added.")
            return redirect('core:template_detail', template_id=category.template.id)
    return redirect('core:template_detail', template_id=category.template.id)