from __future__ import annotations

import logging
from decimal import Decimal

from asgiref.sync import async_to_sync
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.parsers.base import ParserContext
from apps.parsers.manager import ParserManager
from apps.risk.ai import AiRiskAnalyzer
from apps.risk.engine import RiskEngine

from .models import (
    BankruptcyRecord,
    Check,
    CourtCase,
    Debt,
    ParserResult,
    Risk,
    ScrapedAd,
    Source,
)
from .search import CheckSearchIndexer

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, max_retries=3)
def run_property_check(self, check_id: str) -> None:  # type: ignore[no-untyped-def]
    check = Check.objects.select_related("property", "owner").get(id=check_id)
    check.status = Check.Status.RUNNING
    check.started_at = timezone.now()
    check.error_message = ""
    check.save(update_fields=["status", "started_at", "error_message", "updated_at"])
    AuditLog.objects.create(action=AuditLog.Action.PARSER_STARTED, object_type="Check", object_id=check_id)

    try:
        context = ParserContext(
            check_id=str(check.id),
            address=check.property.address,
            cadastral_number=check.property.cadastral_number,
            seller_full_name=check.owner.full_name,
            seller_phone=check.owner.phone,
            seller_email=check.owner.email,
            seller_inn=check.owner.inn,
            region=check.property.region,
        )
        parser_results = async_to_sync(ParserManager().run_all)(context)
        with transaction.atomic():
            ParserResult.objects.filter(property_check=check).delete()
            for result in parser_results:
                ParserResult.objects.create(
                    property_check=check,
                    source=result.source,
                    status=result.status,
                    raw_payload=result.raw_payload,
                    normalized_payload=result.normalized_payload,
                    evidence_url=result.evidence_url,
                    error=result.error,
                    duration_ms=result.duration_ms,
                )
            _materialize_entities(check)
            analysis = RiskEngine().analyse(check.parser_results.all())
            Risk.objects.filter(property_check=check).delete()
            for finding in analysis.findings:
                Risk.objects.create(
                    property_check=check,
                    source=finding["source"],
                    category=finding["category"],
                    severity=finding["severity"],
                    score=Decimal(finding["score"]),
                    title=finding["title"],
                    description=finding["description"],
                    evidence=finding["evidence"],
                )
            ai = AiRiskAnalyzer().analyse(
                {
                    "score": analysis.score,
                    "summary": analysis.summary,
                    "findings": analysis.findings,
                    "timeline": analysis.timeline,
                    "matches": analysis.matches,
                }
            )
            check.risk_score = analysis.score
            check.risk_summary = analysis.summary
            check.ai_summary = ai.summary
            check.legal_recommendations = ai.legal_recommendations
            check.status = Check.Status.COMPLETED
            check.finished_at = timezone.now()
            check.save(
                update_fields=[
                    "risk_score",
                    "risk_summary",
                    "ai_summary",
                    "legal_recommendations",
                    "status",
                    "finished_at",
                    "updated_at",
                ]
            )
        AuditLog.objects.create(action=AuditLog.Action.RISK_ANALYSED, object_type="Check", object_id=check_id)
        try:
            CheckSearchIndexer().index(check)
        except Exception:  # noqa: BLE001 - search indexing is non-critical for check completion.
            logger.exception("check_search_index_failed", extra={"check_id": check_id})
        logger.info("property_check_completed", extra={"check_id": check_id, "risk_score": check.risk_score})
    except Exception as exc:  # noqa: BLE001 - task failure must be persisted for operators.
        check.status = Check.Status.FAILED
        check.error_message = str(exc)
        check.finished_at = timezone.now()
        check.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
        logger.exception("property_check_failed", extra={"check_id": check_id})
        raise


def _materialize_entities(check: Check) -> None:
    CourtCase.objects.filter(property_check=check).delete()
    Debt.objects.filter(property_check=check).delete()
    BankruptcyRecord.objects.filter(property_check=check).delete()
    ScrapedAd.objects.filter(property_check=check).delete()

    for result in check.parser_results.all():
        records = result.normalized_payload.get("records", []) if result.normalized_payload else []
        if result.source in {Source.COURTS, Source.KAD_ARBITR}:
            for record in records:
                CourtCase.objects.create(
                    property_check=check,
                    source=result.source,
                    case_number=record.get("case_number", ""),
                    court_name=record.get("court_name", ""),
                    role=record.get("role", ""),
                    status=record.get("status", ""),
                    url=record.get("url", ""),
                    payload=record,
                )
        elif result.source in {Source.FSSP, Source.ENFORCEMENT, Source.TAX}:
            for record in records:
                Debt.objects.create(
                    property_check=check,
                    source=result.source,
                    amount=record.get("amount"),
                    creditor=record.get("creditor", ""),
                    proceeding_number=record.get("proceeding_number", ""),
                    status=record.get("status", ""),
                    payload=record,
                )
        elif result.source == Source.EFRSB:
            for record in records:
                BankruptcyRecord.objects.create(
                    property_check=check,
                    source=result.source,
                    debtor_name=record.get("debtor_name", ""),
                    case_number=record.get("case_number", ""),
                    stage=record.get("stage", ""),
                    url=record.get("url", ""),
                    payload=record,
                )
        elif result.source in {Source.AVITO, Source.CIAN, Source.DOMCLICK}:
            for record in records:
                ScrapedAd.objects.create(
                    property_check=check,
                    source=result.source,
                    title=record.get("title", ""),
                    url=record.get("url", "https://example.invalid"),
                    price=record.get("price"),
                    address=record.get("address", ""),
                    seller_phone_hash=record.get("seller_phone_hash", ""),
                    payload=record,
                )
