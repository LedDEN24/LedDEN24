from django.contrib import admin

from .models import CashCollectionPoint, CashMeeting


@admin.register(CashMeeting)
class CashMeetingAdmin(admin.ModelAdmin):
    list_display = ("donation", "city", "status", "preferred_time", "scheduled_time", "manager")
    list_filter = ("status", "city")
    search_fields = ("donation__reference", "city", "preferred_place")


admin.site.register(CashCollectionPoint)
