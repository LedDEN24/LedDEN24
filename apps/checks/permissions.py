from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsAnalystOrOwner(BasePermission):
    """Allow owners to read their checks and staff/analysts to operate globally."""

    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore[no-untyped-def]
        if request.user and request.user.is_staff:
            return True
        analyst_group = request.user.groups.filter(name="analyst").exists()
        return analyst_group or obj.requested_by_id == request.user.id
