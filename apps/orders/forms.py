from django import forms
from apps.orders.models import DeliveryOption

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=120, label="Имя")
    phone = forms.CharField(max_length=50, label="Телефон")
    address = forms.CharField(max_length=255, required=False, label="Адрес")
    comment = forms.CharField(widget=forms.Textarea, required=False, label="Комментарий")
    promo_code = forms.CharField(max_length=40, required=False, label="Промокод")
    delivery = forms.ModelChoiceField(queryset=DeliveryOption.objects.filter(is_active=True), required=False, label="Доставка")
    payment_method = forms.ChoiceField(choices=[("cash","Наличными/перевод"),("online","Онлайн")], label="Оплата")
