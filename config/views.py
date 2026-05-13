from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.views.generic import TemplateView

from apps.donations.models import Donation
from apps.news.models import Article
from apps.projects.models import Project


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approved = Donation.objects.filter(status=Donation.Status.APPROVED)
        context.update({
            "featured_projects": Project.objects.filter(status__in=[Project.Status.ACTIVE, Project.Status.FUNDED]).order_by("-is_featured", "-created_at")[:6],
            "latest_news": Article.objects.filter(status=Article.Status.PUBLISHED).order_by("-published_at", "-created_at")[:3],
            "total_collected": approved.aggregate(total=Sum("amount"))["total"] or 0,
            "donors_count": approved.exclude(donor=None).values("donor").distinct().count() + approved.filter(donor=None).count(),
            "completed_projects": Project.objects.filter(status__in=[Project.Status.COMPLETED, Project.Status.FUNDED]).count(),
            "method_stats": approved.values("method").annotate(count=Count("id")),
        })
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["donations"] = self.request.user.donations.select_related("project").all()[:20]
        context["notifications"] = self.request.user.notifications.all()[:10]
        return context


class DonationPageView(TemplateView):
    template_name = "donations/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = Project.objects.filter(status=Project.Status.ACTIVE)
        context["methods"] = Donation.Method.choices
        return context


def robots_txt(request):
    lines = ["User-agent: *", "Allow: /", "Disallow: /admin/", "Sitemap: " + request.build_absolute_uri("/sitemap.xml")]
    return HttpResponse("\n".join(lines), content_type="text/plain")
