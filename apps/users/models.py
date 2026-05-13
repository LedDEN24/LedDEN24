import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        DONOR = "donor", _("Donor")
        MODERATOR = "moderator", _("Moderator")
        FINANCIAL_MANAGER = "financial_manager", _("Financial manager")
        SUPER_ADMIN = "super_admin", _("Super admin")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.DONOR)
    phone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    two_factor_required = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email

    @property
    def is_finance_staff(self) -> bool:
        return self.role in {self.Role.FINANCIAL_MANAGER, self.Role.SUPER_ADMIN} or self.is_superuser


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["token", "expires_at"])]

    def mark_used(self) -> None:
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at >= timezone.now()


class SavedPaymentMethod(models.Model):
    class Method(models.TextChoices):
        CARD = "card", _("Bank card")
        CRYPTO = "crypto", _("Crypto wallet")
        BANK = "bank", _("Bank transfer")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_payment_methods")
    method = models.CharField(max_length=16, choices=Method.choices)
    title = models.CharField(max_length=120)
    masked_details = models.CharField(max_length=160)
    metadata = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.masked_details})"
