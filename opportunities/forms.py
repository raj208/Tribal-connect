from django import forms
from .models import Opportunity


class OpportunitySubmitForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ["title", "description", "opportunity_type", "source_link", "location", "deadline"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }
