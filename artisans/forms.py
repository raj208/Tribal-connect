from django import forms
from .models import ArtisanProfile, ArtisanGalleryImage


class ArtisanProfileForm(forms.ModelForm):
    class Meta:
        model = ArtisanProfile
        fields = [
            "display_name",
            "location",
            "craft_style",
            "bio",
            "maker_story",
            "profile_photo",
            "cover_photo",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "maker_story": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in ("profile_photo", "cover_photo"):
                field.widget.attrs.update({"class": "form-control"})
            elif name in ("bio", "maker_story"):
                field.widget.attrs.update({"class": "form-control"})
            else:
                field.widget.attrs.update({"class": "form-control"})


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = ArtisanGalleryImage
        fields = ["image", "caption"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.update({"class": "form-control"})
        self.fields["caption"].widget.attrs.update({"class": "form-control"})
