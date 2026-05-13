import csv
from io import StringIO

from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone

from apps.donations.models import Donation
from .models import ReportExport


@shared_task
def build_report_export(report_id: int) -> None:
    report = ReportExport.objects.get(pk=report_id)
    report.status = ReportExport.Status.RUNNING
    report.save(update_fields=["status"])
    try:
        buffer = StringIO()
        writer = csv.writer(buffer)
        if report.kind == ReportExport.Kind.DONATIONS:
            writer.writerow(["reference", "amount", "currency", "method", "status", "created_at"])
            for donation in Donation.objects.order_by("-created_at").iterator():
                writer.writerow([donation.reference, donation.amount, donation.currency, donation.method, donation.status, donation.created_at])
        else:
            writer.writerow(["message"])
            writer.writerow([f"{report.kind} export placeholder"])
        report.file.save(f"{report.kind}-{report.pk}.csv", ContentFile(buffer.getvalue().encode("utf-8")), save=False)
        report.status = ReportExport.Status.READY
        report.completed_at = timezone.now()
        report.save(update_fields=["file", "status", "completed_at"])
    except Exception as exc:
        report.status = ReportExport.Status.FAILED
        report.error = str(exc)
        report.save(update_fields=["status", "error"])
