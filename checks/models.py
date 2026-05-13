from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CheckStatus(models.TextChoices):
    PENDING = "pending", "Ожидает обработки"
    RUNNING = "running", "В работе"
    COMPLETED = "completed", "Завершена"
    FAILED = "failed", "Ошибка"


class ParserStatus(models.TextChoices):
    SUCCESS = "success", "Успешно"
    EMPTY = "empty", "Нет данных"
    FAILED = "failed", "Ошибка"
    CACHED = "cached", "Из кэша"


class RiskSeverity(models.TextChoices):
    LOW = "low", "Низкая"
    MEDIUM = "medium", "Средняя"
    HIGH = "high", "Высокая"
    CRITICAL = "critical", "Критическая"


class Check(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="checks",
    )
    address = models.CharField(max_length=512)
    cadastral_number = models.CharField(max_length=128, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    email = models.EmailField(blank=True)
    inn = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=16, choices=CheckStatus.choices, default=CheckStatus.PENDING)
    risk_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Итоговая оценка риска от 0 до 100.",
    )
    report_html = models.TextField(blank=True)
    report_pdf = models.FileField(upload_to="reports/%Y/%m/", blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "checks"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "-created_at")),
            models.Index(fields=("cadastral_number",)),
            models.Index(fields=("inn",)),
        ]

    def __str__(self) -> str:
        return f"Проверка #{self.pk}: {self.address}"

    def get_absolute_url(self) -> str:
        return reverse("report-detail", args=[self.pk])


class ParserResult(TimeStampedModel):
    verification = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="parser_results", db_column="check_id")
    source = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=ParserStatus.choices)
    payload = models.JSONField(default=dict, blank=True)
    matched_fields = models.JSONField(default=list, blank=True)
    error = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(default=0)
    cache_key = models.CharField(max_length=128, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "parser_results"
        ordering = ("source",)
        unique_together = ("verification", "source")
        indexes = [
            models.Index(fields=("source", "status")),
            models.Index(fields=("verification", "source")),
        ]

    def __str__(self) -> str:
        return f"{self.source}: {self.status}"


class Risk(TimeStampedModel):
    verification = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="risks", db_column="check_id")
    parser_result = models.ForeignKey(
        ParserResult,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="risks",
    )
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=16, choices=RiskSeverity.choices)
    weight = models.PositiveSmallIntegerField(default=0)
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "risks"
        ordering = ("-weight", "code")
        indexes = [
            models.Index(fields=("verification", "severity")),
            models.Index(fields=("code",)),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.severity})"


class Property(TimeStampedModel):
    verification = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="properties", db_column="check_id")
    address = models.CharField(max_length=512)
    cadastral_number = models.CharField(max_length=128, blank=True)
    area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=255, blank=True)
    market_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "properties"
        verbose_name_plural = "properties"
        indexes = [models.Index(fields=("cadastral_number",))]

    def __str__(self) -> str:
        return self.cadastral_number or self.address


class Owner(TimeStampedModel):
    verification = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="owners", db_column="check_id")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="owners", null=True, blank=True)
    full_name = models.CharField(max_length=255)
    inn = models.CharField(max_length=32, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    email = models.EmailField(blank=True)
    source = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "owners"
        indexes = [
            models.Index(fields=("full_name",)),
            models.Index(fields=("inn",)),
        ]

    def __str__(self) -> str:
        return self.full_name


class CourtCase(TimeStampedModel):
    verification = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="court_cases", db_column="check_id")
    case_number = models.CharField(max_length=128)
    court_name = models.CharField(max_length=255, blank=True)
    participant = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=128, blank=True)
    claim_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    filed_at = models.DateField(null=True, blank=True)
    source_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "court_cases"
        indexes = [
            models.Index(fields=("case_number",)),
            models.Index(fields=("participant",)),
        ]

    def __str__(self) -> str:
        return self.case_number


class Debt(TimeStampedModel):
    verification = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="debts", db_column="check_id")
    debtor_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    proceeding_number = models.CharField(max_length=128, blank=True)
    bailiff_department = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "debts"
        indexes = [
            models.Index(fields=("debtor_name",)),
            models.Index(fields=("proceeding_number",)),
        ]

    def __str__(self) -> str:
        return f"{self.debtor_name}: {self.amount or 0}"
