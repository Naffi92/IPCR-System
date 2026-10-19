from django import forms
from .models import IPCRTarget, DPCRTarget

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
        
        # Only show DPCR targets that belong to the user's division
        if division:
            self.fields['dpcr_target'].queryset = DPCRTarget.objects.filter(
                dpcr__division=division
            )
        else:
            self.fields['dpcr_target'].queryset = DPCRTarget.objects.none()
            
        # Make dpcr_target optional for now (since OPCR/DPCR creation isn't built yet)
        self.fields['dpcr_target'].required = False
        self.fields['dpcr_target'].empty_label = "-- Not linked to DPCR (Orphan) --"