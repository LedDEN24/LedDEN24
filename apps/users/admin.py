from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailVerificationToken, SavedPaymentMethod, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "role", "email_verified", "is_staff", "date_joined")
    list_filter = ("role", "email_verified", "is_staff", "is_superuser")
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        ("Charity profile", {"fields": ("role", "phone", "country", "city", "avatar", "email_verified", "two_factor_required", "marketing_consent")}),
    )


admin.site.register(EmailVerificationToken)
admin.site.register(SavedPaymentMethod)
