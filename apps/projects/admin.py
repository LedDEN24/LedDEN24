from django.contrib import admin

from .models import Project, ProjectUpdate


class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "goal_amount", "collected_amount", "progress_percent", "featured")
    list_filter = ("status", "featured", "country")
    search_fields = ("title", "summary", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectUpdateInline]
