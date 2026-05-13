from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import asdict, dataclass, field
from typing import Any

import httpx
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ParserInput:
    address: str
    cadastral_number: str = ""
    full_name: str = ""
    phone: str = ""
    email: str = ""
    inn: str = ""

    def searchable_values(self) -> list[str]:
        return [
            value.lower()
            for value in [
                self.address,
                self.cadastral_number,
                self.full_name,
                self.phone,
                self.email,
                self.inn,
            ]
            if value
        ]


@dataclass(slots=True)
class ParserResponse:
    source: str
    status: str = "success"
    matched: bool = False
    confidence: float = 0
    payload: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    fetched_at: Any = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["fetched_at"] = self.fetched_at or timezone.now()
        return data


class BaseParserService:
    source: str = ""
    display_name: str = ""
    base_url: str | None = None
    use_cache: bool = True
    max_retries: int = settings.PARSER_MAX_RETRIES
    timeout_seconds: int = settings.PARSER_HTTP_TIMEOUT_SECONDS
    rate_limit_seconds: float = settings.PARSER_RATE_LIMIT_SECONDS

    _rate_limit_lock = asyncio.Lock()
    _last_request_at = 0.0

    async def parse(self, parser_input: ParserInput) -> ParserResponse:
        cache_key = self.get_cache_key(parser_input)
        if self.use_cache:
            cached = await sync_to_async(cache.get)(cache_key)
            if cached:
                logger.info("Parser cache hit", extra={"source": self.source})
                return ParserResponse(**cached)

        try:
            response = await self._parse_with_retry(parser_input)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Parser failed", extra={"source": self.source})
            response = ParserResponse(
                source=self.source,
                status="error",
                payload={},
                error=str(exc),
                fetched_at=timezone.now(),
            )

        if self.use_cache and response.status == "success":
            await sync_to_async(cache.set)(
                cache_key,
                response.to_dict(),
                timeout=settings.PARSER_CACHE_TTL_SECONDS,
            )
        return response

    async def _parse_with_retry(self, parser_input: ParserInput) -> ParserResponse:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                await self._wait_for_rate_limit()
                payload = await self.fetch_and_parse(parser_input)
                matched, confidence = self.find_matches(parser_input, payload)
                return ParserResponse(
                    source=self.source,
                    status="success",
                    matched=matched,
                    confidence=confidence,
                    payload=payload,
                    fetched_at=timezone.now(),
                )
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                last_error = exc
                logger.warning(
                    "Parser retry",
                    extra={"source": self.source, "attempt": attempt, "error": str(exc)},
                )
                await asyncio.sleep(0.25 * attempt)
        if last_error:
            raise last_error
        raise RuntimeError(f"{self.source} parser returned no response")

    async def fetch_and_parse(self, parser_input: ParserInput) -> dict[str, Any]:
        if not self.base_url:
            return self.build_fallback_payload(parser_input)

        async with httpx.AsyncClient(timeout=self.timeout_seconds, headers=self.headers()) as client:
            response = await client.get(self.base_url, params=self.build_query(parser_input))
            response.raise_for_status()
        return self.extract_payload(response.text, parser_input)

    def build_query(self, parser_input: ParserInput) -> dict[str, str]:
        return {
            "address": parser_input.address,
            "cad": parser_input.cadastral_number,
            "name": parser_input.full_name,
            "inn": parser_input.inn,
        }

    def extract_payload(self, html: str, parser_input: ParserInput) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        return {
            "source_name": self.display_name,
            "raw_text": text[:5000],
            "signals": self.extract_signals(text, parser_input),
        }

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            "source_name": self.display_name,
            "query": asdict(parser_input),
            "signals": [],
            "items": [],
        }

    def extract_signals(self, text: str, parser_input: ParserInput) -> list[dict[str, Any]]:
        normalized = text.lower()
        signals = []
        for value in parser_input.searchable_values():
            if value and value in normalized:
                signals.append({"type": "match", "value": value})
        return signals

    def find_matches(self, parser_input: ParserInput, payload: dict[str, Any]) -> tuple[bool, float]:
        haystack = json.dumps(payload, ensure_ascii=False).lower()
        values = parser_input.searchable_values()
        if not values:
            return False, 0
        matches = sum(1 for value in values if value in haystack)
        confidence = round(matches / len(values), 2)
        return matches > 0, confidence

    async def _wait_for_rate_limit(self) -> None:
        async with self._rate_limit_lock:
            now = asyncio.get_running_loop().time()
            sleep_for = self.rate_limit_seconds - (now - self.__class__._last_request_at)
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            self.__class__._last_request_at = asyncio.get_running_loop().time()

    def headers(self) -> dict[str, str]:
        return {"User-Agent": random.choice(settings.PARSER_USER_AGENTS)}

    def get_cache_key(self, parser_input: ParserInput) -> str:
        digest = hashlib.sha256(
            json.dumps(asdict(parser_input), ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()
        return f"parser:{self.source}:{digest}"
