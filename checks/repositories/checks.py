from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from django.db import transaction

from checks.models import Check, CheckStatus, CourtCase, Debt, Owner, ParserResult, Property, Risk
from checks.parsers.base import ParsedSourceResult


class CheckRepository:
    @staticmethod
    def create_check(*, user, data: dict[str, Any]) -> Check:
        return Check.objects.create(created_by=user, **data)

    @staticmethod
    def get_for_update(check_id: int) -> Check:
        return Check.objects.select_for_update().get(pk=check_id)

    @staticmethod
    def mark_running(check: Check) -> None:
        check.status = CheckStatus.RUNNING
        check.error_message = ""
        check.save(update_fields=("status", "error_message", "updated_at"))

    @staticmethod
    def mark_failed(check: Check, message: str) -> None:
        check.status = CheckStatus.FAILED
        check.error_message = message
        check.save(update_fields=("status", "error_message", "updated_at"))

    @staticmethod
    @transaction.atomic
    def save_results(check: Check, results: Iterable[ParsedSourceResult]) -> list[ParserResult]:
        saved: list[ParserResult] = []
        for result in results:
            parser_result, _ = ParserResult.objects.update_or_create(
                verification=check,
                source=result.source,
                defaults={
                    "status": result.status,
                    "payload": result.payload,
                    "matched_fields": result.matched_fields,
                    "error": result.error,
                    "duration_ms": result.duration_ms,
                    "cache_key": result.cache_key,
                },
            )
            saved.append(parser_result)
        return saved

    @staticmethod
    @transaction.atomic
    def replace_risks(check: Check, risks: Iterable[dict[str, Any]], risk_score: int) -> list[Risk]:
        check.risks.all().delete()
        created = [Risk(verification=check, **risk) for risk in risks]
        risks_created = Risk.objects.bulk_create(created)
        check.risk_score = risk_score
        check.status = CheckStatus.COMPLETED
        check.error_message = ""
        check.save(update_fields=("risk_score", "status", "error_message", "updated_at"))
        return risks_created

    @staticmethod
    @transaction.atomic
    def persist_entities(check: Check, parser_results: Iterable[ParserResult]) -> None:
        check.properties.all().delete()
        check.owners.all().delete()
        check.court_cases.all().delete()
        check.debts.all().delete()

        property_obj = Property.objects.create(
            verification=check,
            address=check.address,
            cadastral_number=check.cadastral_number,
            metadata={"source": "input"},
        )
        if check.full_name:
            Owner.objects.create(
                verification=check,
                property=property_obj,
                full_name=check.full_name,
                inn=check.inn,
                phone=check.phone,
                email=check.email,
                source="input",
            )

        for parser_result in parser_results:
            payload = parser_result.payload or {}
            source = parser_result.source
            for item in payload.get("items", []):
                text = item.get("text", "")
                lowered = text.lower()
                if source in {"kad_arbitr", "russian_courts"} and text:
                    CourtCase.objects.create(
                        verification=check,
                        case_number=item.get("case_number") or f"{source}-{parser_result.pk}",
                        court_name=item.get("court_name", ""),
                        participant=check.full_name,
                        status=item.get("status", ""),
                        claim_amount=_to_decimal(item.get("claim_amount")),
                        source_url=payload.get("source_url", ""),
                        metadata=item,
                    )
                if source == "fssp" or "задолж" in lowered:
                    Debt.objects.create(
                        verification=check,
                        debtor_name=check.full_name or item.get("debtor_name", ""),
                        amount=_to_decimal(item.get("amount")),
                        proceeding_number=item.get("proceeding_number", ""),
                        bailiff_department=item.get("bailiff_department", ""),
                        source_url=payload.get("source_url", ""),
                        metadata=item,
                    )


def _to_decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).replace(" ", "").replace(",", "."))
    except Exception:
        return None
