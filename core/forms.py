from django import forms
from .models import Template, TemplateCategory, TemplateKRA, TemplateColumn
from .models import TemplateGoal, TemplateCategory

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['name', 'description', 'applicable_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Faculty Template 2026'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'applicable_to': forms.Select(attrs={'class': 'form-control'}),
        }

class TemplateCategoryForm(forms.ModelForm):
    class Meta:
        model = TemplateCategory
        fields = ['name', 'default_weight', 'order'] # <-- CHANGED HERE
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), # <-- CHANGED HERE
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TemplateKRAForm(forms.ModelForm):
    class Meta:
        model = TemplateKRA
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TemplateColumnForm(forms.ModelForm):
    class Meta:
        model = TemplateColumn
        fields = ['name', 'phase_availability', 'is_required', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phase_availability': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Add these to the bottom of forms.py

class TemplateCategoryEditForm(forms.ModelForm):
    class Meta:
        model = TemplateCategory
        fields = ['name', 'default_weight', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TemplateColumnEditForm(forms.ModelForm):
    class Meta:
        model = TemplateColumn
        fields = ['name', 'phase_availability', 'is_required', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phase_availability': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TemplateCategoryForm(forms.ModelForm):
    class Meta:
        model = TemplateCategory
        fields = ['name', 'default_weight', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TemplateGoalForm(forms.ModelForm):
    class Meta:
        model = TemplateGoal
        fields = ['name', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TemplateKRAForm(forms.ModelForm):
    class Meta:
        model = TemplateKRA
        fields = ['name', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }