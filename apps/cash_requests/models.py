from __future__ import annotations

from django.conf import settings
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
    preferred_datetime = models.DateTimeField()
    meeting_address = models.CharField(max_length=255, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="cash_meetings")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.REQUESTED)
    manager_notes = models.TextField(blank=True)
    donor_contact = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["preferred_datetime"]
        indexes = [models.Index(fields=["city", "status"])]

    def __str__(self) -> str:
        return f"{self.city} {self.preferred_datetime:%Y-%m-%d %H:%M}"
