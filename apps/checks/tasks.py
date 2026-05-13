from __future__ import annotations

import logging

from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from analysis.aggregator import aggregate_parser_payloads
from analysis.ai import AiRiskAnalyzer
from analysis.risk_engine import RiskEngine
from apps.checks.models import (
    BankruptcyRecord,
    Check,
    CourtCase,
    Debt,
    ParserResult,
    Risk,
    ScrapedAd,
)
from apps.checks.search import SearchIndexer
from parsers.base import ParserInput, ParserStatus
from parsers.infrastructure import DjangoParserInfrastructure
from parsers.manager import ParserManager
from parsers.sources import default_registry

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_property_check(self, check_id: str) -> None:  # noqa: ANN001
    check = Check.objects.select_related("property").prefetch_related("property__owners").get(id=check_id)
    check.mark_running()
    owner = check.property.owners.first()
    parser_input = ParserInput(
        check_id=str(check.id),
        address=check.property.address,
        cadastral_number=check.property.cadastral_number,
        seller_full_name=owner.full_name if owner else "",
        phone=owner.phone if owner else "",
        email=owner.email if owner else "",
        inn=owner.inn if owner else "",
    )
    try:
        infrastructure = DjangoParserInfrastructure.build()
        manager = ParserManager(
            default_registry(),
            infrastructure,
            max_concurrency=settings.PARSER_MAX_CONCURRENCY,
        )
        outputs = async_to_sync(manager.run_all)(parser_input)
        serialized_results = [
            {
                "source": output.source,
                "status": output.status.value,
                "payload": output.payload,
                "error": output.error,
                "duration_ms": output.duration_ms,
                "raw_reference": output.raw_reference,
            }
            for output in outputs
        ]
        aggregated = aggregate_parser_payloads(serialized_results)
        risk_score, findings = RiskEngine().evaluate(aggregated)
        finding_payload = [
            {
                "code": finding.code,
                "title": finding.title,
                "severity": finding.severity.value,
                "score_impact": finding.score_impact,
                "explanation": finding.explanation,
                "evidence": finding.evidence,
                "recommendations": finding.recommendations,
            }
            for finding in findings
        ]
        ai_summary = async_to_sync(AiRiskAnalyzer().analyze)(
            risk_score=risk_score,
            findings=finding_payload,
            aggregated=aggregated,
        )
        _persist_results(check, serialized_results, aggregated, finding_payload, risk_score, ai_summary)
    except Exception as exc:  # noqa: BLE001
        logger.exception("check.failed", extra={"check_id": check_id})
        check.status = Check.Status.FAILED
        check.error = str(exc)
        check.completed_at = timezone.now()
        check.save(update_fields=["status", "error", "completed_at", "updated_at"])
        raise


@transaction.atomic
def _persist_results(
    check: Check,
    parser_results: list[dict],
    aggregated: dict,
    findings: list[dict],
    risk_score: int,
    ai_summary: dict,
) -> None:
    check.parser_results.all().delete()
    check.risks.all().delete()
    check.court_cases.all().delete()
    check.debts.all().delete()
    check.bankruptcy_records.all().delete()
    check.scraped_ads.all().delete()

    ParserResult.objects.bulk_create(
        [
            ParserResult(
                check=check,
                source=result["source"],
                status=result["status"]
                if result["status"] in {status.value for status in ParserStatus}
                else ParserStatus.FAILED.value,
                payload=result["payload"],
                error=result["error"],
                duration_ms=result["duration_ms"],
                raw_reference=result.get("raw_reference", ""),
            )
            for result in parser_results
        ]
    )
    Risk.objects.bulk_create(
        [
            Risk(
                check=check,
                code=finding["code"],
                title=finding["title"],
                severity=finding["severity"],
                score_impact=finding["score_impact"],
                explanation=finding["explanation"],
                evidence=finding["evidence"],
                recommendations=finding["recommendations"],
            )
            for finding in findings
        ]
    )
    _persist_normalized_entities(check, aggregated)
    check.status = Check.Status.COMPLETED
    check.risk_score = risk_score
    check.critical_risks_count = sum(1 for finding in findings if finding["severity"] == "critical")
    check.aggregated_data = aggregated
    check.ai_summary = ai_summary
    check.completed_at = timezone.now()
    check.error = ""
    check.save(
        update_fields=[
            "status",
            "risk_score",
            "critical_risks_count",
            "aggregated_data",
            "ai_summary",
            "completed_at",
            "error",
            "updated_at",
        ]
    )
    SearchIndexer().index_check(check)


def _persist_normalized_entities(check: Check, aggregated: dict) -> None:
    Debt.objects.bulk_create(
        [
            Debt(
                check=check,
                source=item.get("source", ""),
                debtor_name=item.get("debtor_name", ""),
                amount=item.get("amount"),
                proceeding_number=item.get("proceeding_number", ""),
                status=item.get("status", ""),
                payload=item,
            )
            for item in aggregated.get("debts", [])
        ]
    )
    CourtCase.objects.bulk_create(
        [
            CourtCase(
                check=check,
                case_number=item.get("case_number", ""),
                court_name=item.get("court_name", ""),
                role=item.get("role", ""),
                status=item.get("status", ""),
                amount=item.get("amount"),
                filed_at=item.get("filed_at"),
                source_url=item.get("source_url", ""),
                payload=item,
            )
            for item in aggregated.get("court_cases", [])
        ]
    )
    BankruptcyRecord.objects.bulk_create(
        [
            BankruptcyRecord(
                check=check,
                debtor_name=item.get("debtor_name", ""),
                case_number=item.get("case_number", ""),
                stage=item.get("stage", ""),
                published_at=item.get("published_at"),
                source_url=item.get("source_url", ""),
                payload=item,
            )
            for item in aggregated.get("bankruptcy_records", [])
        ]
    )
    ScrapedAd.objects.bulk_create(
        [
            ScrapedAd(
                check=check,
                source=item.get("source", ""),
                title=item.get("title", ""),
                url=item.get("url", ""),
                price=item.get("price"),
                seller_name=item.get("seller_name", ""),
                phone=item.get("phone", ""),
                published_at=item.get("published_at"),
                is_suspicious=item.get("is_suspicious", False),
                payload=item,
            )
            for item in aggregated.get("ads", [])
        ]
    )
