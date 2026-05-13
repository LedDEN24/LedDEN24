from __future__ import annotations

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
    short_description = models.CharField(max_length=320)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=14, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    cover_image = models.ImageField(upload_to="projects/covers/", blank=True, null=True)
    location = models.CharField(max_length=160, blank=True)
    beneficiaries_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    starts_at = models.DateField(null=True, blank=True)
    ends_at = models.DateField(null=True, blank=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        indexes = [models.Index(fields=["status", "is_featured"]), models.Index(fields=["slug"])]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    @property
    def progress_percent(self) -> int:
        if not self.goal_amount:
            return 0
        return min(100, int((self.raised_amount / self.goal_amount) * 100))

    def get_absolute_url(self):
        return reverse("project-detail", kwargs={"slug": self.slug})
