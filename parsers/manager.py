from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from dataclasses import dataclass

from parsers.base import BaseParser, ParserInput, ParserOutput

logger = logging.getLogger(__name__)
type ParserFactory = type[BaseParser]


@dataclass(frozen=True)
class ParserRegistry:
    parsers: dict[str, ParserFactory]

    def selected(self, names: Iterable[str] | None = None) -> list[ParserFactory]:
        if names is None:
            return list(self.parsers.values())
        return [self.parsers[name] for name in names if name in self.parsers]


class ParserManager:
    def __init__(
        self,
        registry: ParserRegistry,
        infrastructure,
        *,
        max_concurrency: int = 8,
    ) -> None:
        self.registry = registry
        self.infrastructure = infrastructure
        self.max_concurrency = max_concurrency

    async def run_all(
        self,
        parser_input: ParserInput,
        *,
        sources: Iterable[str] | None = None,
    ) -> list[ParserOutput]:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def run_parser(parser_cls: ParserFactory) -> ParserOutput:
            async with semaphore:
                parser = parser_cls(self.infrastructure)
                logger.info("parser.started", extra={"source": parser.source, "check_id": parser_input.check_id})
                result = await parser.run(parser_input)
                logger.info(
                    "parser.finished",
                    extra={
                        "source": parser.source,
                        "check_id": parser_input.check_id,
                        "status": result.status,
                        "duration_ms": result.duration_ms,
                    },
                )
                return result

        tasks = [run_parser(parser_cls) for parser_cls in self.registry.selected(sources)]
        if not tasks:
            return []
        return list(await asyncio.gather(*tasks))
