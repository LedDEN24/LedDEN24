from django.contrib import admin

from checks.models import Check, CourtCase, Debt, Owner, ParserResult, Property, Risk


class ParserResultInline(admin.TabularInline):
    model = ParserResult
    extra = 0
    readonly_fields = ("source", "status", "matched", "confidence", "fetched_at", "error")


class RiskInline(admin.TabularInline):
    model = Risk
    extra = 0
    readonly_fields = ("level", "score", "code", "title", "source")


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ("id", "address", "full_name", "status", "risk_level", "risk_score", "created_at")
    list_filter = ("status", "risk_level", "created_at")
    search_fields = ("address", "cadastral_number", "full_name", "phone", "email", "inn")
    readonly_fields = ("risk_score", "risk_level", "summary", "started_at", "completed_at")
    inlines = (ParserResultInline, RiskInline)


@admin.register(ParserResult)
class ParserResultAdmin(admin.ModelAdmin):
    list_display = ("check_request", "source", "status", "matched", "confidence", "fetched_at")
    list_filter = ("source", "status", "matched")
    search_fields = ("check_request__address", "check_request__full_name", "error")


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ("check_request", "level", "score", "code", "title", "source")
    list_filter = ("level", "source")
    search_fields = ("title", "description", "code")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "check_request",
        "address",
        "cadastral_number",
        "property_type",
        "registration_status",
    )
    search_fields = ("address", "cadastral_number")


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("check_request", "full_name", "inn", "phone", "email", "ownership_share")
    search_fields = ("full_name", "inn", "phone", "email")


@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ("check_request", "source", "case_number", "court_name", "participant", "status")
    list_filter = ("source", "status")
    search_fields = ("case_number", "court_name", "participant")


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ("check_request", "source", "debtor_name", "amount", "proceeding_number", "status")
    list_filter = ("source", "status")
    search_fields = ("debtor_name", "proceeding_number")
