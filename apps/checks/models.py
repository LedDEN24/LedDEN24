from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.checks.fields import EncryptedTextField


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Property(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.TextField()
    cadastral_number = models.CharField(max_length=64, db_index=True)
    region = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["cadastral_number"]),
            models.Index(fields=["region"]),
        ]

    def __str__(self) -> str:
        return f"{self.cadastral_number} - {self.address[:80]}"


class Owner(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="owners")
    full_name = EncryptedTextField()
    phone = EncryptedTextField(blank=True)
    email = EncryptedTextField(blank=True)
    inn = EncryptedTextField(blank=True)
    normalized_name_hash = models.CharField(max_length=128, db_index=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["normalized_name_hash"])]

    def __str__(self) -> str:
        return self.full_name


class Check(TimestampedModel):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="property_checks",
        null=True,
        blank=True,
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="checks")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    risk_score = models.PositiveSmallIntegerField(default=0)
    critical_risks_count = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)
    ai_summary = models.JSONField(default=dict, blank=True)
    aggregated_data = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["risk_score"]),
        ]

    def __str__(self) -> str:
        return f"{self.property.cadastral_number} check {self.id}"

    def mark_running(self) -> None:
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_at"])


class ParserResult(TimestampedModel):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="parser_results")
    source = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices)
    payload = models.JSONField(default=dict, blank=True)
    raw_reference = models.CharField(max_length=512, blank=True)
    error = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["check", "source"], name="unique_parser_source_per_check")
        ]
        indexes = [models.Index(fields=["source", "status"])]

    def __str__(self) -> str:
        return f"{self.source}: {self.status}"


class Risk(TimestampedModel):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="risks")
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    severity = models.CharField(max_length=16, choices=Severity.choices)
    score_impact = models.PositiveSmallIntegerField(default=0)
    explanation = models.TextField()
    evidence = models.JSONField(default=dict, blank=True)
    recommendations = models.JSONField(default=list, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self) -> str:
        return f"{self.severity}: {self.title}"


class CourtCase(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="court_cases")
    case_number = models.CharField(max_length=128, db_index=True)
    court_name = models.CharField(max_length=255)
    role = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=128, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    filed_at = models.DateField(null=True, blank=True)
    source_url = models.URLField(max_length=1000, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.case_number


class Debt(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="debts")
    source = models.CharField(max_length=64)
    debtor_name = EncryptedTextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    proceeding_number = models.CharField(max_length=128, blank=True, db_index=True)
    status = models.CharField(max_length=128, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.proceeding_number or self.source


class BankruptcyRecord(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="bankruptcy_records")
    debtor_name = EncryptedTextField()
    case_number = models.CharField(max_length=128, blank=True, db_index=True)
    stage = models.CharField(max_length=128, blank=True)
    published_at = models.DateField(null=True, blank=True)
    source_url = models.URLField(max_length=1000, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.case_number or self.stage


class ScrapedAd(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="scraped_ads")
    source = models.CharField(max_length=64)
    title = models.CharField(max_length=512)
    url = models.URLField(max_length=1000)
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    seller_name = EncryptedTextField(blank=True)
    phone = EncryptedTextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_suspicious = models.BooleanField(default=False)
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.title


class AuditLog(TimestampedModel):
    class Action(models.TextChoices):
        CHECK_CREATED = "check_created", "Check created"
        CHECK_QUEUED = "check_queued", "Check queued"
        PARSER_STARTED = "parser_started", "Parser started"
        PARSER_FINISHED = "parser_finished", "Parser finished"
        REPORT_DOWNLOADED = "report_downloaded", "Report downloaded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=64, choices=Action.choices)
    object_id = models.CharField(max_length=128, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.action}: {self.object_id}"
