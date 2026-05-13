from django.contrib.contenttypes.models import ContentType

from .models import AdminLog


class AdminAuditMiddleware:
    """Records mutating Django admin/API requests made by staff members."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.user.is_staff and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            AdminLog.objects.create(
                actor=request.user,
                action=AdminLog.Action.UPDATE,
                content_type=ContentType.objects.get_for_model(request.user),
                object_id=str(request.user.pk),
                message=f"{request.method} {request.path}",
                metadata={"status_code": response.status_code},
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        return response
