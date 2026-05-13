from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        DONOR = "donor", _("Donor")
        MODERATOR = "moderator", _("Moderator")
        FINANCIAL_MANAGER = "financial_manager", _("Financial Manager")
        SUPER_ADMIN = "super_admin", _("Super Admin")

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.DONOR)
    phone = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=128, blank=True)
    preferred_language = models.CharField(max_length=8, default="ru")
    email_verified = models.BooleanField(default=False)
    saved_payment_details = models.JSONField(default=dict, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["email"]

    @property
    def is_finance_staff(self) -> bool:
        return self.is_superuser or self.role in {self.Role.SUPER_ADMIN, self.Role.FINANCIAL_MANAGER}

    @property
    def is_content_staff(self) -> bool:
        return self.is_superuser or self.role in {self.Role.SUPER_ADMIN, self.Role.MODERATOR}
