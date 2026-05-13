from __future__ import annotations

import asyncio
import logging

from celery import shared_task

from checks.models import Check
from checks.repositories import CheckRepository
from checks.services.parsers import AsyncParserManager
from checks.services.risk_analyzer import RiskAnalyzer


logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True, max_retries=3)
def run_check_parsing(self, check_id: int) -> dict:
    repository = CheckRepository()
    check = Check.objects.get(pk=check_id)
    repository.mark_running(check)

    try:
        results = asyncio.run(AsyncParserManager().run(check))
        repository.save_parser_results(check, results)
        summary = RiskAnalyzer().analyze(results)
        repository.save_risk_summary(check, summary)
        logger.info("Check parsing completed", extra={"check_id": check_id, "score": summary.score})
        return {"check_id": check_id, "status": "completed", "risk_score": summary.score}
    except Exception as exc:  # noqa: BLE001
        repository.mark_failed(check, str(exc))
        logger.exception("Check parsing failed", extra={"check_id": check_id})
        raise
