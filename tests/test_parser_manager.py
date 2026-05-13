from __future__ import annotations

import unittest
from typing import Any

from parsers.base import BaseParser, ParserInput
from parsers.manager import ParserManager, ParserRegistry


class InMemoryInfrastructure:
    http = None

    def __init__(self) -> None:
        self.cache: dict[str, dict[str, Any]] = {}

    async def before_request(self, source: str) -> None:
        return None

    async def cache_get(self, key: str) -> dict[str, Any] | None:
        return self.cache.get(key)

    async def cache_set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        self.cache[key] = value

    async def solve_captcha(self, source: str, challenge: dict[str, Any]) -> str:
        return "token"


class DemoParser(BaseParser):
    source = "demo"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {"cadastral_number": parser_input.cadastral_number}


class ParserManagerTests(unittest.IsolatedAsyncioTestCase):
    async def test_runs_registered_parser(self) -> None:
        manager = ParserManager(
            ParserRegistry({"demo": DemoParser}),
            InMemoryInfrastructure(),
            max_concurrency=1,
        )

        results = await manager.run_all(
            ParserInput(
                check_id="check-1",
                address="Москва",
                cadastral_number="77:01:0000000:1",
                seller_full_name="Иванов И.И.",
            )
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, "demo")
        self.assertEqual(results[0].payload["cadastral_number"], "77:01:0000000:1")


if __name__ == "__main__":
    unittest.main()
