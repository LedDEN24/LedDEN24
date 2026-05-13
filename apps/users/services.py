from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


def build_email_confirmation_url(user, request=None) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("api-email-confirm", kwargs={"uidb64": uid, "token": token})
    if request:
        return request.build_absolute_uri(path)
    return path


def send_email_confirmation(user, request=None) -> None:
    url = build_email_confirmation_url(user, request)
    send_mail(
        subject="Confirm your Global Care account",
        message=f"Please confirm your email: {url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
