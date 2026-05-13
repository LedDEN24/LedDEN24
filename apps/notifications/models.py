from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "in_app", _("In app")
        EMAIL = "email", "Email"
        TELEGRAM = "telegram", "Telegram"

    class Level(models.TextChoices):
        INFO = "info", _("Info")
        SUCCESS = "success", _("Success")
        WARNING = "warning", _("Warning")
        ERROR = "error", _("Error")

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=180)
    message = models.TextField()
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.IN_APP)
    level = models.CharField(max_length=16, choices=Level.choices, default=Level.INFO)
    link = models.URLField(blank=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "read_at"])]

    def __str__(self) -> str:
        return self.title
