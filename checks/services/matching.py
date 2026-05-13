from __future__ import annotations

import re
from dataclasses import dataclass

from checks.models import Check, ParserResult


@dataclass(frozen=True)
class MatchSignal:
    field: str
    value: str


class MatchService:
    @staticmethod
    def find_matches(check: Check, parser_result: ParserResult) -> list[MatchSignal]:
        payload = parser_result.payload or {}
        haystack = str(payload).lower()
        candidates = {
            "address": check.address,
            "cadastral_number": check.cadastral_number,
            "full_name": check.full_name,
            "phone": _normalize_phone(check.phone),
            "email": check.email,
            "inn": check.inn,
        }
        matches = []
        normalized_haystack = _normalize_phone(haystack)
        for field, value in candidates.items():
            if value and value.lower() in haystack:
                matches.append(MatchSignal(field=field, value=value))
            elif field == "phone" and value and value in normalized_haystack:
                matches.append(MatchSignal(field=field, value=value))
        return matches


def _normalize_phone(value: str) -> str:
    return re.sub(r"\D+", "", value or "")
