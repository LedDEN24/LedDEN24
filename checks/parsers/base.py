from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, ClassVar

import httpx
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]


@dataclass(frozen=True)
class ParserQuery:
    address: str
    cadastral_number: str = ""
    full_name: str = ""
    phone: str = ""
    email: str = ""
    inn: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "address": self.address,
            "cadastral_number": self.cadastral_number,
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "inn": self.inn,
        }


@dataclass
class ParsedSourceResult:
    source: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)
    matched_fields: list[str] = field(default_factory=list)
    error: str = ""
    duration_ms: int = 0
    cache_key: str = ""


class ParserError(Exception):
    pass


class AsyncRateLimiter:
    def __init__(self, rate_per_second: float) -> None:
        self.min_interval = 1 / rate_per_second if rate_per_second > 0 else 0
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        async with self._lock:
            elapsed = time.monotonic() - self._last_call
            delay = self.min_interval - elapsed
            if delay > 0:
                await asyncio.sleep(delay)
            self._last_call = time.monotonic()


class BaseParser:
    source_name: ClassVar[str]
    base_url: ClassVar[str]
    cache_ttl: ClassVar[int] = settings.PARSER_CACHE_TTL
    max_retries: ClassVar[int] = settings.PARSER_MAX_RETRIES
    timeout: ClassVar[float] = settings.PARSER_REQUEST_TIMEOUT
    rate_limit_per_second: ClassVar[float] = settings.PARSER_RATE_LIMIT_PER_SECOND

    def __init__(self) -> None:
        self.rate_limiter = AsyncRateLimiter(self.rate_limit_per_second)
        self.logger = logging.getLogger(f"checks.parsers.{self.source_name}")

    async def parse(self, query: ParserQuery) -> ParsedSourceResult:
        started = time.monotonic()
        cache_key = self.build_cache_key(query)
        cached = await sync_to_async(cache.get)(cache_key)
        if cached:
            self.logger.info("cache hit", extra={"source": self.source_name})
            cached["duration_ms"] = self._duration_ms(started)
            cached["cache_key"] = cache_key
            cached["status"] = "cached"
            return ParsedSourceResult(**cached)

        try:
            payload = await self.fetch_and_parse(query)
            status = "success" if payload.get("items") or payload.get("summary") else "empty"
            result = ParsedSourceResult(
                source=self.source_name,
                status=status,
                payload=payload,
                matched_fields=self.match_fields(payload, query),
                duration_ms=self._duration_ms(started),
                cache_key=cache_key,
            )
            await sync_to_async(cache.set)(cache_key, result.__dict__, self.cache_ttl)
            return result
        except Exception as exc:
            self.logger.exception("parser failed")
            return ParsedSourceResult(
                source=self.source_name,
                status="failed",
                payload={},
                error=str(exc),
                duration_ms=self._duration_ms(started),
                cache_key=cache_key,
            )

    async def fetch_and_parse(self, query: ParserQuery) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                await self.rate_limiter.wait()
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(
                        self.build_url(query),
                        params=self.build_params(query),
                        headers=self.build_headers(),
                    )
                    response.raise_for_status()
                return self.extract_data(response.text, query)
            except (httpx.HTTPError, ParserError) as exc:
                last_error = exc
                self.logger.warning(
                    "attempt failed",
                    extra={"source": self.source_name, "attempt": attempt, "error": str(exc)},
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))
        raise ParserError(str(last_error) if last_error else "unknown parser error")

    def build_cache_key(self, query: ParserQuery) -> str:
        digest = hashlib.sha256(
            json.dumps({"source": self.source_name, "query": query.as_dict()}, sort_keys=True).encode()
        ).hexdigest()
        return f"parser:{self.source_name}:{digest}"

    def build_url(self, query: ParserQuery) -> str:
        return self.base_url

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {k: v for k, v in query.as_dict().items() if v}

    def build_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru,en;q=0.9",
        }

    def extract_data(self, html: str, query: ParserQuery) -> dict[str, Any]:
        raise NotImplementedError

    def match_fields(self, payload: dict[str, Any], query: ParserQuery) -> list[str]:
        haystack = json.dumps(payload, ensure_ascii=False).lower()
        matched: list[str] = []
        for field, value in query.as_dict().items():
            if value and value.lower() in haystack:
                matched.append(field)
        return matched

    @staticmethod
    def _duration_ms(started: float) -> int:
        return int((time.monotonic() - started) * 1000)


class KeywordHtmlParser(BaseParser):
    risk_keywords: ClassVar[tuple[str, ...]] = ()
    result_selector: ClassVar[str] = "body"

    def extract_data(self, html: str, query: ParserQuery) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        nodes = soup.select(self.result_selector) or [soup]
        text_blocks = [" ".join(node.get_text(" ", strip=True).split()) for node in nodes]
        items = [{"text": text[:2000]} for text in text_blocks if text]
        haystack = " ".join(text_blocks).lower()
        found_keywords = [keyword for keyword in self.risk_keywords if keyword.lower() in haystack]
        return {
            "source_url": self.build_url(query),
            "items": items[:20],
            "summary": {
                "total_items": len(items),
                "risk_keywords": found_keywords,
            },
        }
