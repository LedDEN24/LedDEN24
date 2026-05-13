from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def create_notification(recipient, title: str, message: str, level: str = "info", link: str = "") -> Notification:
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        level=level,
        link=link,
    )
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.pk}",
            {
                "type": "notification.message",
                "payload": {
                    "id": notification.pk,
                    "title": notification.title,
                    "message": notification.message,
                    "level": notification.level,
                    "link": notification.link,
                },
            },
        )
    return notification
