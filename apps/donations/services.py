from decimal import Decimal

from django.db import transaction
from django.db.models import F

from apps.adminpanel.models import AdminLog
from apps.projects.models import Project
from .models import Donation, DonationAllocation


HIGH_VALUE_THRESHOLD = Decimal("10000.00")


def score_suspicious_operation(donation: Donation) -> Donation:
    score = 0
    reasons = []
    if donation.amount >= HIGH_VALUE_THRESHOLD:
        score += 45
        reasons.append("high_value")
    if donation.is_anonymous and donation.amount >= Decimal("1000.00"):
        score += 25
        reasons.append("anonymous_high_value")
    if donation.method in {Donation.Method.BTC, Donation.Method.ETH, Donation.Method.USDT_TRC20, Donation.Method.USDT_ERC20}:
        score += 10
        reasons.append("crypto")
    donation.suspicious_score = min(score, 100)
    donation.suspicious_reason = ",".join(reasons)
    donation.status = Donation.Status.CHECKING if score >= 50 else donation.status
    donation.save(update_fields=["suspicious_score", "suspicious_reason", "status", "updated_at"])
    return donation


@transaction.atomic
def approve_donation(donation: Donation, reviewer) -> Donation:
    donation = Donation.objects.select_for_update().select_related("project").get(pk=donation.pk)
    if donation.status == Donation.Status.APPROVED:
        return donation
    donation.approve(reviewer)
    if donation.project_id:
        Project.objects.filter(pk=donation.project_id).update(collected_amount=F("collected_amount") + donation.amount)
        DonationAllocation.objects.get_or_create(
            donation=donation,
            project=donation.project,
            defaults={"amount": donation.amount, "allocated_by": reviewer},
        )
    AdminLog.objects.create(actor=reviewer, action="donation.approved", object_type="Donation", object_id=str(donation.pk))
    return donation


@transaction.atomic
def reject_donation(donation: Donation, reviewer, reason: str) -> Donation:
    donation = Donation.objects.select_for_update().get(pk=donation.pk)
    donation.reject(reviewer, reason)
    AdminLog.objects.create(
        actor=reviewer,
        action="donation.rejected",
        object_type="Donation",
        object_id=str(donation.pk),
        metadata={"reason": reason},
    )
    return donation
