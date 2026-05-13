from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections.abc import Iterable

from django.conf import settings

from .base import BaseParser, ParserContext, ParserResultDTO
from .infrastructure import ParserCache
from .registry import build_parsers

logger = logging.getLogger(__name__)


class ParserManager:
    def __init__(
        self,
        parsers: Iterable[BaseParser] | None = None,
        cache: ParserCache | None = None,
        max_concurrency: int | None = None,
    ) -> None:
        self.parsers = list(parsers) if parsers is not None else build_parsers()
        self.cache = cache or ParserCache()
        concurrency = max_concurrency if max_concurrency is not None else settings.PARSER_MAX_CONCURRENCY
        self.max_concurrency = int(concurrency)

    async def run_all(self, context: ParserContext) -> list[ParserResultDTO]:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def run(parser: BaseParser) -> ParserResultDTO:
            async with semaphore:
                cache_key = self._cache_key(parser, context)
                cached = self.cache.get(cache_key)
                if cached:
                    return ParserResultDTO(**cached)
                result = await parser.execute(context)
                if result.status in {"success", "empty"}:
                    self.cache.set(cache_key, result.__dict__)
                return result

        logger.info("parser_manager_started", extra={"check_id": context.check_id, "count": len(self.parsers)})
        results = await asyncio.gather(*(run(parser) for parser in self.parsers))
        logger.info("parser_manager_finished", extra={"check_id": context.check_id, "count": len(results)})
        return list(results)

    @staticmethod
    def _cache_key(parser: BaseParser, context: ParserContext) -> str:
        payload = {
            "source": parser.source,
            "address": context.address,
            "cadastral_number": context.cadastral_number,
            "seller_full_name": context.seller_full_name,
            "seller_inn": context.seller_inn,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return f"parser:{parser.source}:{digest}"
