from __future__ import annotations

import logging

from celery import shared_task

from checks.services.check_runner import run_check_pipeline

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def process_check(self, check_id: int) -> int:
    logger.info("processing check", extra={"check_id": check_id})
    return run_check_pipeline(check_id)
