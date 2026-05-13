from __future__ import annotations

from rest_framework.permissions import BasePermission


class Role:
    ANALYST = "analyst"
    MANAGER = "manager"
    ADMIN = "admin"


class IsAnalystOrManager(BasePermission):
    """RBAC gate for due-diligence operations."""

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        return user.groups.filter(name__in=[Role.ANALYST, Role.MANAGER, Role.ADMIN]).exists()
