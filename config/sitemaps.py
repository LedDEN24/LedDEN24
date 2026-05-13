from django.contrib.sitemaps import Sitemap

from apps.news.models import Article
from apps.projects.models import Project


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return ["home", "donate"]

    def location(self, item):
        return {"home": "/", "donate": "/donate/"}[item]


class ProjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Project.objects.filter(status__in=[Project.Status.ACTIVE, Project.Status.FUNDED, Project.Status.COMPLETED])


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Article.objects.filter(status=Article.Status.PUBLISHED)
