from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Sum
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework import permissions, views, viewsets
from rest_framework.response import Response

from apps.donations.models import Donation
from apps.projects.models import Project
from apps.users.permissions import IsFinanceManager

from .models import AdminLog
from .serializers import AdminLogSerializer


class AdminDashboardView(UserPassesTestMixin, TemplateView):
    template_name = "adminpanel/dashboard.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_finance_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_donations"] = Donation.objects.filter(status__in=[Donation.Status.PENDING, Donation.Status.CHECKING]).select_related("project")[:10]
        context["projects"] = Project.objects.all()[:6]
        return context


class AdminStatsAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsFinanceManager]

    def get(self, request):
        today = timezone.now().date()
        donations = Donation.objects.all()
        return Response({
            "total_collected": donations.filter(status=Donation.Status.APPROVED).aggregate(total=Sum("amount"))["total"] or 0,
            "pending_count": donations.filter(status__in=[Donation.Status.PENDING, Donation.Status.CHECKING]).count(),
            "donors_count": donations.exclude(donor=None).values("donor").distinct().count(),
            "completed_projects": Project.objects.filter(status=Project.Status.COMPLETED).count(),
            "today_donations": donations.filter(created_at__date=today).count(),
            "by_method": list(donations.values("method").annotate(count=Count("id")).order_by("method")),
        })


class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdminLog.objects.select_related("actor", "content_type")
    serializer_class = AdminLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceManager]
    filterset_fields = ["action", "actor"]
    search_fields = ["message", "object_id", "actor__email"]
