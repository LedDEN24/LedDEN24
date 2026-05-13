from django.contrib import admin

from .models import Check, CourtCase, Debt, Owner, ParserResult, Property, Risk


class ParserResultInline(admin.TabularInline):
    model = ParserResult
    extra = 0
    readonly_fields = ("source", "status", "duration_ms", "fetched_at")
    can_delete = False


class RiskInline(admin.TabularInline):
    model = Risk
    extra = 0
    readonly_fields = ("code", "severity", "weight")


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("id", "address", "full_name", "inn", "status", "risk_score", "created_at")
    list_filter = ("status", "risk_score", "created_at")
    search_fields = ("address", "cadastral_number", "full_name", "phone", "email", "inn")
    readonly_fields = ("created_at", "updated_at")
    inlines = (ParserResultInline, RiskInline)


@admin.register(ParserResult)
class ParserResultAdmin(admin.ModelAdmin):
    list_display = ("verification", "source", "status", "duration_ms", "fetched_at")
    list_filter = ("source", "status", "fetched_at")
    search_fields = ("verification__address", "source", "error")
    readonly_fields = ("created_at", "updated_at", "fetched_at")


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ("verification", "code", "title", "severity", "weight")
    list_filter = ("severity", "code")
    search_fields = ("title", "description", "code")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("address", "cadastral_number", "area", "market_price")
    search_fields = ("address", "cadastral_number")


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "inn", "phone", "email", "source")
    search_fields = ("full_name", "inn", "phone", "email")


@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ("case_number", "court_name", "participant", "status", "claim_amount")
    search_fields = ("case_number", "court_name", "participant")


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ("debtor_name", "amount", "proceeding_number", "bailiff_department")
    search_fields = ("debtor_name", "proceeding_number", "bailiff_department")
