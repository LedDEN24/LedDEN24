from __future__ import annotations

import csv
from io import StringIO

from django.core.files.base import ContentFile

from apps.donations.models import Donation

from .models import Report


def generate_donations_csv(*, user, filters: dict | None = None) -> Report:
    filters = filters or {}
    queryset = Donation.objects.select_related("donor", "project").all()
    if status := filters.get("status"):
        queryset = queryset.filter(status=status)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["public_id", "amount", "currency", "method", "status", "project", "created_at"])
    for donation in queryset.iterator():
        writer.writerow([donation.public_id, donation.amount, donation.currency, donation.method, donation.status, donation.project.title if donation.project else "", donation.created_at.isoformat()])
    report = Report.objects.create(title="Donations export", report_type=Report.Type.DONATIONS, filters=filters, generated_by=user)
    report.file.save("donations.csv", ContentFile(output.getvalue().encode("utf-8")), save=True)
    return report
