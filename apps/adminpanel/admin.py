from django.contrib import admin

from .models import AdminLog


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "object_type", "object_id", "ip_address", "created_at")
    list_filter = ("action", "object_type", "created_at")
    search_fields = ("action", "actor__email", "object_id", "user_agent")
    readonly_fields = ("actor", "action", "object_type", "object_id", "ip_address", "user_agent", "metadata", "created_at")
