from django.conf import settings
from django.db import models
from django.urls import reverse


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CheckStatus(models.TextChoices):
    PENDING = "pending", "Ожидает"
    RUNNING = "running", "В работе"
    COMPLETED = "completed", "Завершена"
    FAILED = "failed", "Ошибка"


class ParserSource(models.TextChoices):
    FSSP = "fssp", "ФССП"
    EFRSB = "efrsb", "ЕФРСБ"
    KAD_ARBITR = "kad_arbitr", "КАД Арбитр"
    RF_COURTS = "rf_courts", "Суды РФ"
    ROSREESTR = "rosreestr", "Росреестр"
    CADASTRAL_MAP = "cadastral_map", "Кадастровая карта"
    AVITO = "avito", "Avito"
    CIAN = "cian", "Cian"
    DOMCLICK = "domclick", "Domclick"
    NEWS = "news", "Новости и СМИ"
    TELEGRAM = "telegram", "Telegram"
    DEVELOPERS = "developers", "Проблемные застройщики"


class RiskLevel(models.TextChoices):
    LOW = "low", "Низкий"
    MEDIUM = "medium", "Средний"
    HIGH = "high", "Высокий"
    CRITICAL = "critical", "Критический"


class Check(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="checks")
    address = models.CharField("Адрес", max_length=512)
    cadastral_number = models.CharField("Кадастровый номер", max_length=64, blank=True, db_index=True)
    full_name = models.CharField("ФИО", max_length=255)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("Email", blank=True)
    inn = models.CharField("ИНН", max_length=12, blank=True, db_index=True)
    status = models.CharField(max_length=16, choices=CheckStatus.choices, default=CheckStatus.PENDING)
    risk_score = models.PositiveSmallIntegerField(default=0)
    risk_level = models.CharField(max_length=16, choices=RiskLevel.choices, default=RiskLevel.LOW)
    summary = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["risk_level", "risk_score"]),
        ]
        verbose_name = "Проверка"
        verbose_name_plural = "Проверки"

    def __str__(self) -> str:
        return f"Проверка #{self.pk}: {self.address}"

    def get_absolute_url(self) -> str:
        return reverse("checks:report", kwargs={"pk": self.pk})


class ParserResult(TimestampedModel):
    check_request = models.ForeignKey(
        Check, on_delete=models.CASCADE, related_name="parser_results", db_column="check_id"
    )
    source = models.CharField(max_length=32, choices=ParserSource.choices)
    status = models.CharField(max_length=16, default="success")
    matched = models.BooleanField(default=False)
    confidence = models.FloatField(default=0)
    payload = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    fetched_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("check_request", "source")
        ordering = ("source",)
        verbose_name = "Результат парсера"
        verbose_name_plural = "Результаты парсеров"

    def __str__(self) -> str:
        return f"{self.get_source_display()} / {self.check_request_id}"


class Risk(TimestampedModel):
    check_request = models.ForeignKey(
        Check, on_delete=models.CASCADE, related_name="risks", db_column="check_id"
    )
    source = models.CharField(max_length=32, choices=ParserSource.choices, blank=True)
    level = models.CharField(max_length=16, choices=RiskLevel.choices)
    score = models.PositiveSmallIntegerField()
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField()
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-score", "code")
        verbose_name = "Риск"
        verbose_name_plural = "Риски"

    def __str__(self) -> str:
        return f"{self.title} ({self.score})"


class Property(TimestampedModel):
    check_request = models.ForeignKey(
        Check, on_delete=models.CASCADE, related_name="properties", db_column="check_id"
    )
    address = models.CharField(max_length=512)
    cadastral_number = models.CharField(max_length=64, blank=True, db_index=True)
    area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    property_type = models.CharField(max_length=128, blank=True)
    registration_status = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"


class Owner(TimestampedModel):
    check_request = models.ForeignKey(
        Check, on_delete=models.CASCADE, related_name="owners", db_column="check_id"
    )
    full_name = models.CharField(max_length=255)
    inn = models.CharField(max_length=12, blank=True, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    ownership_share = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Собственник"
        verbose_name_plural = "Собственники"


class CourtCase(TimestampedModel):
    check_request = models.ForeignKey(
        Check, on_delete=models.CASCADE, related_name="court_cases", db_column="check_id"
    )
    source = models.CharField(max_length=32, choices=ParserSource.choices)
    case_number = models.CharField(max_length=128, blank=True, db_index=True)
    court_name = models.CharField(max_length=255, blank=True)
    participant = models.CharField(max_length=255, blank=True)
    claim_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=128, blank=True)
    url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Судебное дело"
        verbose_name_plural = "Судебные дела"


class Debt(TimestampedModel):
    check_request = models.ForeignKey(
        Check, on_delete=models.CASCADE, related_name="debts", db_column="check_id"
    )
    source = models.CharField(max_length=32, choices=ParserSource.choices)
    debtor_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    proceeding_number = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Задолженность"
        verbose_name_plural = "Задолженности"
