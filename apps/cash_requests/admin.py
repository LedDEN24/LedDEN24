from django.contrib import admin

from .models import CashMeeting


@admin.register(CashMeeting)
class CashMeetingAdmin(admin.ModelAdmin):
    list_display = ("donation", "city", "preferred_datetime", "manager", "status")
    list_filter = ("city", "status", "manager")
    search_fields = ("donation__public_id", "city", "donor_contact")
