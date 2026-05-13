from __future__ import annotations

import asyncio
import logging

from django.db import transaction

from checks.models import Check
from checks.parsers import ParserManager
from checks.parsers.base import ParserQuery
from checks.repositories import CheckRepository
from checks.reports.generator import ReportGenerator
from checks.services.risk_analyzer import RiskAnalyzer

logger = logging.getLogger(__name__)


def run_check_pipeline(check_id: int) -> int:
    with transaction.atomic():
        check = CheckRepository.get_for_update(check_id)
        CheckRepository.mark_running(check)

    try:
        query = ParserQuery(
            address=check.address,
            cadastral_number=check.cadastral_number,
            full_name=check.full_name,
            phone=check.phone,
            email=check.email,
            inn=check.inn,
        )
        parser_results_data = asyncio.run(ParserManager().run_all(query))
        parser_results = CheckRepository.save_results(check, parser_results_data)
        CheckRepository.persist_entities(check, parser_results)
        risk_score, risks = RiskAnalyzer().analyze(check, parser_results)
        CheckRepository.replace_risks(check, risks, risk_score)
        ReportGenerator().generate(check)
        return risk_score
    except Exception as exc:
        logger.exception("check pipeline failed", extra={"check_id": check_id})
        check.refresh_from_db()
        CheckRepository.mark_failed(check, str(exc))
        raise
