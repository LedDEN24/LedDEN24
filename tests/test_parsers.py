import pytest

from checks.parsers.base import BaseParser, ParsedSourceResult, ParserQuery
from checks.parsers.manager import ParserManager


class StubParser(BaseParser):
    source_name = "stub"
    base_url = "https://example.test/"

    async def parse(self, query):
        return ParsedSourceResult(
            source=self.source_name,
            status="success",
            payload={"items": [{"text": query.address}], "summary": {"total_items": 1}},
            matched_fields=["address"],
        )

    def extract_data(self, html, query):
        return {}


@pytest.mark.asyncio
async def test_parser_manager_runs_registered_parsers():
    results = await ParserManager([StubParser]).run_all(ParserQuery(address="Москва, Тверская 1"))

    assert len(results) == 1
    assert results[0].source == "stub"
    assert results[0].matched_fields == ["address"]
