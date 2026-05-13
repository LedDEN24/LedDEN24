from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render
from rest_framework import viewsets

from apps.cash_requests.models import CashMeeting
from apps.donations.models import Donation
from apps.projects.models import Project
from .models import AdminLog
from .permissions import IsModeratorOrAbove
from .serializers import AdminLogSerializer


class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminLogSerializer
    permission_classes = [IsModeratorOrAbove]
    queryset = AdminLog.objects.select_related("actor")


@staff_member_required
def dashboard(request):
    donation_stats = Donation.objects.values("status").annotate(count=Count("id"), total=Sum("amount"))
    context = {
        "raised": Donation.objects.filter(status=Donation.Status.APPROVED).aggregate(total=Sum("amount"))["total"] or 0,
        "pending": Donation.objects.filter(status__in=[Donation.Status.PENDING, Donation.Status.CHECKING]).count(),
        "projects": Project.objects.count(),
        "cash_requests": CashMeeting.objects.exclude(status=CashMeeting.Status.COMPLETED).count(),
        "donation_stats": donation_stats,
        "recent_donations": Donation.objects.select_related("project", "donor")[:10],
        "admin_logs": AdminLog.objects.select_related("actor")[:10],
    }
    return render(request, "adminpanel/dashboard.html", context)
