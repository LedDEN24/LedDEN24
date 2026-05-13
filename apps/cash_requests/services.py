from __future__ import annotations

from apps.notifications.services import create_notification

from .models import CashMeeting


def assign_cash_manager(meeting: CashMeeting, manager) -> CashMeeting:
    meeting.manager = manager
    meeting.status = CashMeeting.Status.SCHEDULED
    meeting.save(update_fields=["manager", "status", "updated_at"])
    if meeting.donation.donor_id:
        create_notification(
            recipient=meeting.donation.donor,
            title="Cash meeting scheduled",
            body=f"A manager has been assigned for your cash donation in {meeting.city}.",
            severity="info",
        )
    return meeting
