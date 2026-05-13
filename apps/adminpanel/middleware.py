from .models import AdminLog


class AdminAuditMiddleware:
    """Record mutating admin dashboard actions without logging sensitive payloads."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.path.startswith("/dashboard/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            AdminLog.objects.create(
                actor=request.user,
                action=f"http.{request.method.lower()}",
                object_type="dashboard",
                object_id=request.path,
                ip_address=self._client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
                metadata={"status_code": response.status_code},
            )
        return response

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
