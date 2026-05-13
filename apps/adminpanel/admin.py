from django.contrib import admin

from .models import AdminLog


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "message", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("actor__email", "message", "object_id")
    readonly_fields = ("actor", "action", "content_type", "object_id", "message", "metadata", "ip_address", "created_at")
