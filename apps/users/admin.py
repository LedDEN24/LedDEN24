from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "email_verified", "is_staff", "created_at")
    list_filter = ("role", "email_verified", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (("Charity profile", {"fields": ("role", "phone", "city", "preferred_language", "email_verified", "saved_payment_details", "notification_settings", "failed_login_attempts", "locked_until")}),)
