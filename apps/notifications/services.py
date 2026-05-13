from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def create_notification(*, recipient=None, title: str, body: str = "", severity: str = "info", channel: str = "in_app", action_url: str = "", metadata: dict | None = None) -> Notification:
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        body=body,
        severity=severity,
        channel=channel,
        action_url=action_url,
        metadata=metadata or {},
    )
    if recipient_id := getattr(recipient, "id", None):
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            f"user_{recipient_id}",
            {
                "type": "notification.message",
                "payload": {
                    "id": notification.id,
                    "title": notification.title,
                    "body": notification.body,
                    "severity": notification.severity,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )
    return notification
