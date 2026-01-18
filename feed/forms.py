from django import forms
from .models import BasePost, Comment, Report


class BasePostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Comma-separated tags (max 5). Example: festival, folklore, education",
    )

    class Meta:
        model = BasePost
        fields = ["post_type", "title", "body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 6})}

    def clean_tags(self):
        raw = (self.cleaned_data.get("tags") or "").strip()
        if not raw:
            return []
        parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
        # unique, max 5
        uniq = []
        for p in parts:
            if p not in uniq:
                uniq.append(p)
        if len(uniq) > 5:
            raise forms.ValidationError("Maximum 5 tags allowed.")
        for t in uniq:
            if len(t) > 40:
                raise forms.ValidationError("A tag is too long (max 40 chars).")
        return uniq


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a comment..."}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional note"})}
