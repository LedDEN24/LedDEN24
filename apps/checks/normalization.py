from __future__ import annotations

import hashlib
import re


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def normalize_phone(value: str) -> str:
    return re.sub(r"\D+", "", value)


def stable_hash(value: str) -> str:
    normalized = normalize_text(value)
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode()).hexdigest()
