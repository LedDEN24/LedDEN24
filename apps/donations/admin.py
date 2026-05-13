from django.contrib import admin

from .models import Donation, DonationAllocation, Transaction


class TransactionInline(admin.StackedInline):
    model = Transaction
    extra = 0


class DonationAllocationInline(admin.TabularInline):
    model = DonationAllocation
    extra = 0


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("reference", "amount", "currency", "method", "status", "project", "created_at")
    list_filter = ("status", "method", "currency", "created_at")
    search_fields = ("reference", "donor_email", "donor_name")
    readonly_fields = ("reference", "suspicious_score", "suspicious_reason", "created_at", "updated_at")
    inlines = [TransactionInline, DonationAllocationInline]


admin.site.register(Transaction)
admin.site.register(DonationAllocation)
