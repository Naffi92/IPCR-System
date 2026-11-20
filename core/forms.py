from django import forms
from .models import Template, TemplateCategory, TemplateKRA, TemplateColumn
from .models import TemplateGoal, TemplateCategory
from .models import RatingPeriod, PositionCategoryWeight

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
        fields = ['name', 'phase_availability', 'data_type', 'is_required', 'order'] # <-- ADDED
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phase_availability': forms.Select(attrs={'class': 'form-control'}),
            'data_type': forms.Select(attrs={'class': 'form-control'}), # <-- ADDED
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

class RatingPeriodForm(forms.ModelForm):
    class Meta:
        model = RatingPeriod
        fields = ['name', 'target_start', 'target_end', 'midyear_date', 'accomplishment_start', 'accomplishment_end', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'target_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'target_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'midyear_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'accomplishment_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'accomplishment_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PositionCategoryWeightForm(forms.ModelForm):
    class Meta:
        model = PositionCategoryWeight
        fields = ['position', 'category', 'weight_percentage']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'weight_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class TemplateSelectionForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=Template.objects.none(), 
        empty_label="Select a Template...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super().__init__(*args, **kwargs)
        if user_type:
            self.fields['template'].queryset = Template.objects.filter(evaluation_type=user_type)
