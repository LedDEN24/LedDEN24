from django import forms

from .models import DemoRequest


class DemoRequestForm(forms.Form):
    name = forms.CharField(
        label="Имя",
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Как к вам обращаться",
                "autocomplete": "name",
            }
        ),
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "name@company.ru",
                "autocomplete": "email",
            }
        ),
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "placeholder": "+7 (999) 123-45-67",
                "autocomplete": "tel",
            }
        ),
    )
    company = forms.CharField(
        label="Компания",
        max_length=180,
        widget=forms.TextInput(
            attrs={
                "placeholder": "ООО Ромашка",
                "autocomplete": "organization",
            }
        ),
    )
    role = forms.CharField(
        label="Роль",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Юрист, HR, комплаенс, собственник",
                "autocomplete": "organization-title",
            }
        ),
    )
    message = forms.CharField(
        label="Что нужно показать на демо",
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Например: проверка контрагентов, сценарий найма, legal/compliance-процесс.",
                "rows": 5,
            }
        ),
    )
    agree = forms.BooleanField(
        label="Я ознакомлен(а) с политикой ПДн и согласен(на) на обработку данных для обработки заявки",
    )

    def save(self) -> DemoRequest:
        data = self.cleaned_data
        return DemoRequest.objects.create(
            company_name=data["company"],
            contact_name=data["name"],
            email=data["email"],
            phone=data["phone"],
            role=data.get("role", ""),
            message=data.get("message", ""),
            agreed_to_personal_data=data["agree"],
        )
