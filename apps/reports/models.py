from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ReportExport(models.Model):
    class Kind(models.TextChoices):
        DONATIONS = "donations", _("Donations")
        PROJECTS = "projects", _("Projects")
        CASH = "cash", _("Cash requests")
        AUDIT = "audit", _("Audit log")

    class Status(models.TextChoices):
        QUEUED = "queued", _("Queued")
        RUNNING = "running", _("Running")
        READY = "ready", _("Ready")
        FAILED = "failed", _("Failed")

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    kind = models.CharField(max_length=24, choices=Kind.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    filters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="reports/", blank=True, null=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.kind} export ({self.status})"
