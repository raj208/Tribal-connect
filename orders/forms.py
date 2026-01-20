from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=20)
    address_line1 = forms.CharField(max_length=200)
    address_line2 = forms.CharField(max_length=200, required=False)
    city = forms.CharField(max_length=80)
    state = forms.CharField(max_length=80)
    pincode = forms.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({"class": "form-control"})
