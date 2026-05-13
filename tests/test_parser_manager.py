from __future__ import annotations

from typing import Any

import pytest

from apps.checks.models import ParserResult, Source
from apps.parsers.base import BaseParser, ParserContext, ParserResultDTO
from apps.parsers.manager import ParserManager


class MemoryCache:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        return self.values.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        self.values[key] = value


class DummyParser(BaseParser):
    source = Source.MEDIA

    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, context: ParserContext) -> ParserResultDTO:
        self.calls += 1
        return ParserResultDTO(
            source=self.source,
            status=ParserResult.Status.SUCCESS,
            normalized_payload={"configured": True, "matches_count": 1, "records": [{"title": "news"}]},
        )


@pytest.mark.asyncio
async def test_parser_manager_caches_successful_results() -> None:
    parser = DummyParser()
    context = ParserContext(
        check_id="1",
        address="Москва",
        cadastral_number="77:01:1:1",
        seller_full_name="Иванов Иван",
    )
    manager = ParserManager(parsers=[parser], cache=MemoryCache(), max_concurrency=1)

    first = await manager.run_all(context)
    second = await manager.run_all(context)

    assert first[0].normalized_payload["matches_count"] == 1
    assert second[0].normalized_payload["matches_count"] == 1
    assert parser.calls == 1
