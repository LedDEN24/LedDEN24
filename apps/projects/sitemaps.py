from django.contrib.sitemaps import Sitemap

from .models import Project


class ProjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Project.objects.filter(status__in=[Project.Status.ACTIVE, Project.Status.FUNDED, Project.Status.COMPLETED])

    def lastmod(self, obj):
        return obj.updated_at
