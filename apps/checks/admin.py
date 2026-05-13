from __future__ import annotations

from django.contrib import admin

from .models import (
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
    search_fields = ("cadastral_number", "normalized_address")


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("normalized_full_name", "created_at")
    search_fields = ("normalized_full_name", "inn_hash")


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "risk_score", "created_at", "finished_at")
    list_filter = ("status", "created_at")


admin.site.register(ParserResult)
admin.site.register(Risk)
admin.site.register(CourtCase)
admin.site.register(Debt)
admin.site.register(BankruptcyRecord)
admin.site.register(ScrapedAd)
