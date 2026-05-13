from django import forms

from checks.models import Check


class CheckForm(forms.ModelForm):
    class Meta:
        model = Check
        fields = ("address", "cadastral_number", "full_name", "phone", "email", "inn")
        widgets = {
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Москва, ..."}),
            "cadastral_number": forms.TextInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "inn": forms.TextInput(attrs={"class": "form-control"}),
        }
