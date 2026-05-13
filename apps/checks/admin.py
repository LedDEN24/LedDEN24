from __future__ import annotations

from django.contrib import admin

from apps.checks.models import (
    AuditLog,
    BankruptcyRecord,
    Check,
    CourtCase,
    Debt,
    Owner,
    ParserResult,
    Property,
    Risk,
    ScrapedAd,
)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("cadastral_number", "region", "created_at")
    search_fields = ("cadastral_number", "address")


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "status", "risk_score", "created_at")
    list_filter = ("status",)


admin.site.register(Owner)
admin.site.register(ParserResult)
admin.site.register(Risk)
admin.site.register(CourtCase)
admin.site.register(Debt)
admin.site.register(BankruptcyRecord)
admin.site.register(ScrapedAd)
admin.site.register(AuditLog)
