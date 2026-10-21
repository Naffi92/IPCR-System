from django import forms
from django.forms import modelformset_factory
from .models import IPCRTarget, DPCRTarget, BehavioralRating, BehavioralDimension, CriticalIncident
from .models import OPCR, OPCRTarget, DPCR, DPCRTarget


class IPCRTargetForm(forms.ModelForm):
    class Meta:
        model = IPCRTarget
        fields = [
            'output', 
            'dpcr_target', 
            'weight', 
            'quality_target', 
            'efficiency_target', 
            'timeliness_target'
        ]
        widgets = {
            'output': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Submit 3 research papers'}),
            'dpcr_target': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'max': '100'}),
            'quality_target': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Quality success indicator'}),
            'efficiency_target': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Efficiency success indicator'}),
            'timeliness_target': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Timeliness success indicator'}),
        }

    def __init__(self, *args, **kwargs):
        division = kwargs.pop('division', None)
        super().__init__(*args, **kwargs)
        
        if division:
            self.fields['dpcr_target'].queryset = DPCRTarget.objects.filter(
                dpcr__division=division
            )
        else:
            self.fields['dpcr_target'].queryset = DPCRTarget.objects.none()
            
        self.fields['dpcr_target'].required = False
        self.fields['dpcr_target'].empty_label = "-- Not linked to DPCR (Orphan) --"


AppraisalFormSet = modelformset_factory(
    IPCRTarget,
    fields=[
        'quality_actual', 'efficiency_actual', 'timeliness_actual', 
        'quality_rating', 'efficiency_rating', 'timeliness_rating'
    ],
    extra=0,
    widgets={
        'quality_actual': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'efficiency_actual': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'timeliness_actual': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        'efficiency_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        'timeliness_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
    }
)

class BehavioralRatingForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, max_value=5, required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5})
    )
    
    class Meta:
        model = BehavioralRating
        fields = ['rating', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }

BehavioralRatingFormSet = modelformset_factory(
    BehavioralRating,
    form=BehavioralRatingForm,
    extra=0
)

class CriticalIncidentForm(forms.ModelForm):
    class Meta:
        model = CriticalIncident
        fields = ['incident_type', 'date_occurred', 'description']
        widgets = {
            'incident_type': forms.Select(attrs={'class': 'form-control'}),
            'date_occurred': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class OPCRForm(forms.ModelForm):
    class Meta:
        model = OPCR
        fields = ['office_name', 'rating_period']
        widgets = {
            'office_name': forms.TextInput(attrs={'class': 'form-control'}),
            'rating_period': forms.Select(attrs={'class': 'form-control'}),
        }

OPCRTargetFormSet = modelformset_factory(
    OPCRTarget,
    fields=['mfo', 'success_indicator', 'weight'],
    extra=3,
    widgets={
        'mfo': forms.TextInput(attrs={'class': 'form-control'}),
        'success_indicator': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
    }
)

class DPCRForm(forms.ModelForm):
    class Meta:
        model = DPCR
        fields = ['division', 'rating_period']
        widgets = {
            'division': forms.Select(attrs={'class': 'form-control'}),
            'rating_period': forms.Select(attrs={'class': 'form-control'}),
        }

DPCRTargetFormSet = modelformset_factory(
    DPCRTarget,
    fields=['output', 'success_indicator', 'weight', 'opcr_target'],
    extra=3,
    widgets={
        'output': forms.TextInput(attrs={'class': 'form-control'}),
        'success_indicator': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        'opcr_target': forms.Select(attrs={'class': 'form-control'}),
    }
)