from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Контакты и реквизиты", {"fields": ("phone", "inn")}),)
    list_display = ("username", "email", "phone", "inn", "is_staff", "is_active")
    search_fields = ("username", "email", "phone", "inn")
