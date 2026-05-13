from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "goal_amount", "raised_amount", "progress_percent", "is_featured", "created_at")
    list_filter = ("status", "is_featured", "currency")
    search_fields = ("title", "short_description", "location")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("raised_amount", "progress_percent", "created_at", "updated_at")
