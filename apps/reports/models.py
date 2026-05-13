from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    class Type(models.TextChoices):
        DONATIONS = "donations", _("Donations")
        PROJECTS = "projects", _("Projects")
        FINANCE = "finance", _("Finance")
        AUDIT = "audit", _("Audit")

    title = models.CharField(max_length=180)
    report_type = models.CharField(max_length=24, choices=Type.choices)
    filters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="reports/", blank=True, null=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]
