from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable

from checks.models import Check
from checks.services.parsers.base import BaseParserService, ParserInput
from checks.services.parsers.registry import get_parser_classes


logger = logging.getLogger(__name__)


class AsyncParserManager:
    def __init__(
        self,
        parsers: Iterable[BaseParserService] | None = None,
        concurrency: int = 4,
    ) -> None:
        self.parsers = list(parsers) if parsers is not None else [cls() for cls in get_parser_classes()]
        self.semaphore = asyncio.Semaphore(concurrency)

    async def run(self, check: Check) -> list[dict]:
        parser_input = ParserInput(
            address=check.address,
            cadastral_number=check.cadastral_number,
            full_name=check.full_name,
            phone=check.phone,
            email=check.email,
            inn=check.inn,
        )
        tasks = [self._run_parser(parser, parser_input) for parser in self.parsers]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        results = []
        for parser, response in zip(self.parsers, responses, strict=True):
            if isinstance(response, Exception):
                logger.exception("Unhandled parser error", extra={"source": parser.source})
                results.append(
                    {
                        "source": parser.source,
                        "status": "error",
                        "matched": False,
                        "confidence": 0,
                        "payload": {},
                        "error": str(response),
                    }
                )
            else:
                results.append(response.to_dict())
        return results

    async def _run_parser(self, parser: BaseParserService, parser_input: ParserInput):
        async with self.semaphore:
            return await parser.parse(parser_input)
