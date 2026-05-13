from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CashMeeting(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", _("Requested")
        SCHEDULED = "scheduled", _("Scheduled")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    donation = models.OneToOneField("donations.Donation", on_delete=models.CASCADE, related_name="cash_meeting")
    city = models.CharField(max_length=120)
    preferred_place = models.CharField(max_length=220)
    preferred_time = models.DateTimeField()
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="cash_meetings")
    scheduled_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    manager_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["city", "status"])]

    def __str__(self) -> str:
        return f"{self.donation.reference} cash meeting in {self.city}"


class CashCollectionPoint(models.Model):
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["city", "address"]

    def __str__(self) -> str:
        return f"{self.city}: {self.address}"
