from django.contrib.sitemaps import Sitemap

from .models import NewsArticle


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_at
