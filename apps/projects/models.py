from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        FUNDED = "funded", _("Funded")
        COMPLETED = "completed", _("Completed")
        ARCHIVED = "archived", _("Archived")

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    summary = models.CharField(max_length=320)
    description = models.TextField()
    country = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True)
    cover_image = models.ImageField(upload_to="projects/", blank=True, null=True)
    goal_amount = models.DecimalField(max_digits=14, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    beneficiaries_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.ACTIVE)
    featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    starts_at = models.DateField(blank=True, null=True)
    ends_at = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "-created_at"]
        indexes = [
            models.Index(fields=["status", "featured"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def progress_percent(self) -> int:
        if not self.goal_amount:
            return 0
        return min(100, int((self.collected_amount / self.goal_amount) * 100))

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.title


class ProjectUpdate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="updates")
    title = models.CharField(max_length=220)
    body = models.TextField()
    image = models.ImageField(upload_to="project-updates/", blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return f"{self.project}: {self.title}"
