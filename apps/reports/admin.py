from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "report_type", "generated_by", "generated_at")
    list_filter = ("report_type", "generated_at")
    search_fields = ("title", "generated_by__email")
