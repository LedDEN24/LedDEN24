from __future__ import annotations

import base64
import hashlib
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _derive_local_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    key = settings.FIELD_ENCRYPTION_KEY
    if not key:
        if settings.DEBUG:
            key = _derive_local_key(settings.SECRET_KEY).decode("ascii")
        else:
            raise ImproperlyConfigured("FIELD_ENCRYPTION_KEY must be set in production")
    return Fernet(key.encode("ascii"))


class EncryptedTextField(models.TextField):
    """TextField encrypted at rest using Fernet before database persistence."""

    description = "Encrypted text"

    def get_prep_value(self, value: Any) -> str | None:
        if value is None or value == "":
            return value
        if isinstance(value, str) and value.startswith("gAAAAA"):
            return value
        return get_fernet().encrypt(str(value).encode("utf-8")).decode("ascii")

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> str | None:
        return self.to_python(value)

    def to_python(self, value: Any) -> str | None:
        if value is None or value == "":
            return value
        if not isinstance(value, str):
            return str(value)
        try:
            return get_fernet().decrypt(value.encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError):
            return value
