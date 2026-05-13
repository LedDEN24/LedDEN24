from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from rest_framework import filters, permissions, viewsets

from apps.donations.models import Donation
from apps.news.models import NewsArticle
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "summary", "description", "country", "city"]
    ordering_fields = ["created_at", "goal_amount", "collected_amount"]

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


def home(request):
    projects = Project.objects.filter(status=Project.Status.ACTIVE).order_by("-featured", "-created_at")[:6]
    news = NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED).order_by("-published_at")[:3]
    totals = Donation.objects.filter(status=Donation.Status.APPROVED).aggregate(total=Sum("amount"))
    stats = {
        "raised": totals["total"] or 0,
        "donors": Donation.objects.filter(status=Donation.Status.APPROVED).values("donor_email").distinct().count(),
        "completed": Project.objects.filter(status=Project.Status.COMPLETED).count(),
    }
    return render(request, "pages/home.html", {"projects": projects, "news": news, "stats": stats})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, status__in=[Project.Status.ACTIVE, Project.Status.FUNDED, Project.Status.COMPLETED])
    return render(request, "pages/project_detail.html", {"project": project})


class RobotsView(TemplateView):
    template_name = "robots.txt"
    content_type = "text/plain"
