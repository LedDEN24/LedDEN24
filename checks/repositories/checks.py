from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from checks.models import Check, CheckStatus, CourtCase, Debt, Owner, ParserResult, Property, Risk
from checks.services.risk_analyzer import RiskFinding, RiskSummary


class CheckRepository:
    @transaction.atomic
    def mark_running(self, check: Check) -> Check:
        check.status = CheckStatus.RUNNING
        check.started_at = timezone.now()
        check.save(update_fields=["status", "started_at", "updated_at"])
        return check

    @transaction.atomic
    def save_parser_results(self, check: Check, results: Iterable[dict]) -> list[ParserResult]:
        saved: list[ParserResult] = []
        for result in results:
            parser_result, _ = ParserResult.objects.update_or_create(
                check_request=check,
                source=result["source"],
                defaults={
                    "status": result.get("status", "success"),
                    "matched": result.get("matched", False),
                    "confidence": result.get("confidence", 0),
                    "payload": result.get("payload", {}),
                    "error": result.get("error", ""),
                    "fetched_at": result.get("fetched_at", timezone.now()),
                },
            )
            saved.append(parser_result)
            self._materialize_entities(check, result)
        return saved

    @transaction.atomic
    def save_risk_summary(self, check: Check, summary: RiskSummary) -> Check:
        check.risks.all().delete()
        for finding in summary.findings:
            self._create_risk(check, finding)
        check.risk_score = summary.score
        check.risk_level = summary.level
        check.summary = summary.text
        check.status = CheckStatus.COMPLETED
        check.completed_at = timezone.now()
        check.save(
            update_fields=[
                "risk_score",
                "risk_level",
                "summary",
                "status",
                "completed_at",
                "updated_at",
            ]
        )
        return check

    @transaction.atomic
    def mark_failed(self, check: Check, error: str) -> Check:
        check.status = CheckStatus.FAILED
        check.summary = error
        check.completed_at = timezone.now()
        check.save(update_fields=["status", "summary", "completed_at", "updated_at"])
        return check

    def _materialize_entities(self, check: Check, result: dict) -> None:
        payload = result.get("payload") or {}
        for item in payload.get("properties", []):
            Property.objects.update_or_create(
                check_request=check,
                cadastral_number=item.get("cadastral_number", "") or check.cadastral_number,
                defaults={
                    "address": item.get("address", check.address),
                    "area": self._decimal_or_none(item.get("area")),
                    "property_type": item.get("property_type", ""),
                    "registration_status": item.get("registration_status", ""),
                    "metadata": item,
                },
            )
        for item in payload.get("owners", []):
            Owner.objects.update_or_create(
                check_request=check,
                full_name=item.get("full_name", check.full_name),
                inn=item.get("inn", check.inn),
                defaults={
                    "phone": item.get("phone", ""),
                    "email": item.get("email", ""),
                    "ownership_share": item.get("ownership_share", ""),
                    "metadata": item,
                },
            )
        for item in payload.get("court_cases", []):
            CourtCase.objects.update_or_create(
                check_request=check,
                source=result["source"],
                case_number=item.get("case_number", ""),
                defaults={
                    "court_name": item.get("court_name", ""),
                    "participant": item.get("participant", ""),
                    "claim_amount": self._decimal_or_none(item.get("claim_amount")),
                    "status": item.get("status", ""),
                    "url": item.get("url", ""),
                    "metadata": item,
                },
            )
        for item in payload.get("debts", []):
            Debt.objects.update_or_create(
                check_request=check,
                source=result["source"],
                proceeding_number=item.get("proceeding_number", ""),
                defaults={
                    "debtor_name": item.get("debtor_name", check.full_name),
                    "amount": self._decimal_or_none(item.get("amount")),
                    "status": item.get("status", ""),
                    "metadata": item,
                },
            )

    def _create_risk(self, check: Check, finding: RiskFinding) -> Risk:
        return Risk.objects.create(
            check_request=check,
            source=finding.source,
            level=finding.level,
            score=finding.score,
            code=finding.code,
            title=finding.title,
            description=finding.description,
            evidence=finding.evidence,
        )

    def _decimal_or_none(self, value: object) -> Decimal | None:
        if value in (None, ""):
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None
