from __future__ import annotations

from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _fernet() -> Fernet:
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", "")
    if not key:
        msg = "FIELD_ENCRYPTION_KEY must be configured for encrypted model fields."
        raise ImproperlyConfigured(msg)
    return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedTextField(models.TextField):
    """TextField encrypted at rest with Fernet before hitting the database."""

    description = "Encrypted text"

    def get_prep_value(self, value: Any) -> Any:
        if value in (None, ""):
            return value
        prepared = super().get_prep_value(value)
        token = _fernet().encrypt(str(prepared).encode())
        return token.decode()

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> Any:
        if value in (None, ""):
            return value
        try:
            return _fernet().decrypt(str(value).encode()).decode()
        except InvalidToken:
            return value

    def to_python(self, value: Any) -> Any:
        if value in (None, ""):
            return value
        if isinstance(value, str) and value.startswith("gAAAA"):
            try:
                return _fernet().decrypt(value.encode()).decode()
            except InvalidToken:
                return value
        return value
