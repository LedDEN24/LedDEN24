from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.fields import EncryptedTextField
from apps.core.models import TimeStampedModel


class Source(models.TextChoices):
    FSSP = "fssp", "ФССП"
    EFRSB = "efrsb", "ЕФРСБ"
    KAD_ARBITR = "kad_arbitr", "КАД Арбитр"
    COURTS = "courts", "Суды РФ"
    ROSREESTR = "rosreestr", "Росреестр"
    CADASTRAL_MAP = "cadastral_map", "Публичная кадастровая карта"
    TAX = "tax", "Налоговые данные"
    ENFORCEMENT = "enforcement", "Исполнительные производства"
    AVITO = "avito", "Avito"
    CIAN = "cian", "Cian"
    DOMCLICK = "domclick", "Domclick"
    TELEGRAM_FORUMS = "telegram_forums", "Telegram/форумы"
    PROBLEM_DEVELOPERS = "problem_developers", "Проблемные застройщики"
    FRAUD_REGISTRIES = "fraud_registries", "Базы мошенников"
    MEDIA = "media", "Новости и СМИ"


class Property(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.TextField()
    normalized_address = models.TextField(blank=True, db_index=True)
    cadastral_number = models.CharField(max_length=64, db_index=True)
    region = models.CharField(max_length=128, blank=True, db_index=True)
    property_type = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = "properties"
        indexes = [
            models.Index(fields=["cadastral_number"]),
            models.Index(fields=["region", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.cadastral_number} {self.address[:80]}"


class Owner(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = EncryptedTextField()
    phone = EncryptedTextField(blank=True)
    email = EncryptedTextField(blank=True)
    inn = EncryptedTextField(blank=True)
    normalized_full_name = models.CharField(max_length=255, blank=True, db_index=True)
    inn_hash = models.CharField(max_length=128, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.normalized_full_name or "encrypted-owner"


class Check(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="property_checks",
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="checks")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="checks")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.QUEUED)
    risk_score = models.PositiveSmallIntegerField(default=0)
    risk_summary = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    legal_recommendations = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    request_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["risk_score"]),
        ]

    def __str__(self) -> str:
        return f"check:{self.id}:{self.status}"


class ParserResult(TimeStampedModel):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        EMPTY = "empty", "Empty"
        FAILED = "failed", "Failed"
        CAPTCHA_REQUIRED = "captcha_required", "Captcha required"
        RATE_LIMITED = "rate_limited", "Rate limited"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="parser_results")
    source = models.CharField(max_length=64, choices=Source.choices, db_index=True)
    status = models.CharField(max_length=32, choices=Status.choices)
    raw_payload = models.JSONField(default=dict, blank=True)
    normalized_payload = models.JSONField(default=dict, blank=True)
    evidence_url = models.URLField(blank=True)
    error = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["source", "-created_at"]
        unique_together = [("property_check", "source")]
        indexes = [models.Index(fields=["source", "status", "created_at"])]

    def __str__(self) -> str:
        return f"{self.source}:{self.status}"


class Risk(TimeStampedModel):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="risks")
    source = models.CharField(max_length=64, choices=Source.choices, blank=True)
    category = models.CharField(max_length=128, db_index=True)
    severity = models.CharField(max_length=32, choices=Severity.choices, db_index=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    title = models.CharField(max_length=255)
    description = models.TextField()
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-score", "category"]
        indexes = [models.Index(fields=["severity", "category"])]


class CourtCase(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="court_cases")
    source = models.CharField(max_length=64, choices=Source.choices, default=Source.COURTS)
    case_number = models.CharField(max_length=128, db_index=True)
    court_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=128, blank=True)
    claim_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=128, blank=True)
    filed_at = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True)
    payload = models.JSONField(default=dict, blank=True)


class Debt(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="debts")
    source = models.CharField(max_length=64, choices=Source.choices, default=Source.FSSP)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    creditor = models.CharField(max_length=255, blank=True)
    proceeding_number = models.CharField(max_length=128, blank=True, db_index=True)
    status = models.CharField(max_length=128, blank=True)
    payload = models.JSONField(default=dict, blank=True)


class BankruptcyRecord(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="bankruptcy_records")
    source = models.CharField(max_length=64, choices=Source.choices, default=Source.EFRSB)
    debtor_name = models.CharField(max_length=255, blank=True)
    inn_hash = models.CharField(max_length=128, blank=True, db_index=True)
    case_number = models.CharField(max_length=128, blank=True, db_index=True)
    stage = models.CharField(max_length=128, blank=True)
    published_at = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True)
    payload = models.JSONField(default=dict, blank=True)


class ScrapedAd(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_check = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="scraped_ads")
    source = models.CharField(max_length=64, choices=Source.choices)
    title = models.CharField(max_length=255, blank=True)
    url = models.URLField()
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    address = models.TextField(blank=True)
    seller_phone_hash = models.CharField(max_length=128, blank=True, db_index=True)
    first_seen_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
