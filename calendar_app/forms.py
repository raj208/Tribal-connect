from django import forms
from .models import CulturalEvent


class CulturalEventForm(forms.ModelForm):
    class Meta:
        model = CulturalEvent
        fields = ["title", "description", "category", "date", "location"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "date": forms.DateInput(attrs={"type": "date"}),
        }
