from django.contrib import admin

from .models import ReportExport


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ("kind", "status", "requested_by", "created_at", "completed_at")
    list_filter = ("kind", "status")
    readonly_fields = ("created_at", "completed_at")
