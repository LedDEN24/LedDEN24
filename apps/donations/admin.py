from django.contrib import admin, messages

from .models import Donation, Transaction
from .services import approve_donation, reject_donation


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ("created_at", "checked_at")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("public_id", "amount", "currency", "method", "status", "project", "risk_score", "created_at")
    list_filter = ("status", "method", "currency", "is_anonymous")
    search_fields = ("public_id", "payment_reference", "donor_email", "donor_name")
    readonly_fields = ("public_id", "payment_reference", "risk_score", "suspicious_reason", "approved_at", "created_at", "updated_at")
    inlines = [TransactionInline]
    actions = ["approve_selected", "reject_selected"]

    @admin.action(description="Approve selected donations")
    def approve_selected(self, request, queryset):
        for donation in queryset:
            approve_donation(donation, request.user)
        self.message_user(request, f"Approved {queryset.count()} donation(s).", messages.SUCCESS)

    @admin.action(description="Reject selected donations")
    def reject_selected(self, request, queryset):
        for donation in queryset:
            reject_donation(donation, request.user, "Rejected from admin bulk action")
        self.message_user(request, f"Rejected {queryset.count()} donation(s).", messages.WARNING)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("donation", "gateway", "status", "amount", "currency", "created_at")
    list_filter = ("gateway", "status", "currency")
    search_fields = ("donation__public_id", "external_id")
