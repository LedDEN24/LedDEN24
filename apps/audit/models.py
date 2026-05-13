from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    class Action(models.TextChoices):
        CHECK_CREATED = "check_created", "Check created"
        PARSER_STARTED = "parser_started", "Parser started"
        PARSER_FINISHED = "parser_finished", "Parser finished"
        RISK_ANALYSED = "risk_analysed", "Risk analysed"
        REPORT_GENERATED = "report_generated", "Report generated"
        API_ACCESS = "api_access", "API access"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    action = models.CharField(max_length=64, choices=Action.choices, db_index=True)
    object_type = models.CharField(max_length=128, blank=True)
    object_id = models.CharField(max_length=128, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["object_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action}:{self.object_type}:{self.object_id}"
