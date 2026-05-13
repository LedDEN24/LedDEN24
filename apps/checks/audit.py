from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from apps.checks.models import AuditLog


def write_audit_log(
    *,
    request: HttpRequest | None,
    action: AuditLog.Action,
    object_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    actor = getattr(request, "user", None) if request is not None else None
    if actor is not None and not actor.is_authenticated:
        actor = None
    AuditLog.objects.create(
        actor=actor,
        action=action,
        object_id=object_id,
        ip_address=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
        metadata=metadata or {},
    )


def _client_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
