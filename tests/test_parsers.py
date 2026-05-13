import pytest

from checks.services.parsers import AsyncParserManager
from checks.services.parsers.base import BaseParserService, ParserInput


class MatchingParser(BaseParserService):
    source = "news"
    display_name = "Test"
    rate_limit_seconds = 0

    def build_fallback_payload(self, parser_input: ParserInput):
        return {"text": f"{parser_input.full_name} {parser_input.inn}", "items": []}


@pytest.mark.asyncio
async def test_parser_finds_matches():
    parser = MatchingParser()
    result = await parser.parse(ParserInput(address="Москва", full_name="Иванов Иван", inn="1234567890"))

    assert result.status == "success"
    assert result.matched is True
    assert result.confidence > 0


@pytest.mark.django_db
def test_parser_manager_runs_all_sources(user, check):
    manager = AsyncParserManager(parsers=[MatchingParser()], concurrency=1)

    import asyncio

    results = asyncio.run(manager.run(check))

    assert len(results) == 1
    assert results[0]["source"] == "news"
