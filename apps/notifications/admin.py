from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "channel", "severity", "read_at", "created_at")
    list_filter = ("channel", "severity", "read_at")
    search_fields = ("title", "body", "recipient__email")
