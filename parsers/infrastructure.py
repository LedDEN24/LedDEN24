from __future__ import annotations

import asyncio
import itertools
import logging
import random
from dataclasses import dataclass
from typing import Any

import httpx
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
]


class ProxyManager:
    def __init__(self, proxies: list[str] | None = None) -> None:
        self._proxies = proxies or settings.PROXY_POOL
        self._iterator = itertools.cycle(self._proxies) if self._proxies else None

    def next_proxy(self) -> str | None:
        if self._iterator is None:
            return None
        return next(self._iterator)


class AsyncRateLimiter:
    def __init__(self, per_minute: int) -> None:
        self._interval = 60 / max(per_minute, 1)
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        async with self._lock:
            loop = asyncio.get_running_loop()
            elapsed = loop.time() - self._last_call
            if elapsed < self._interval:
                await asyncio.sleep(self._interval - elapsed)
            self._last_call = loop.time()


class CaptchaService:
    """Abstraction over external captcha providers or human-in-the-loop queues."""

    async def solve(self, source: str, challenge: dict[str, Any]) -> str:
        logger.warning("captcha.solve.requested", extra={"source": source, "challenge": challenge})
        raise RuntimeError(f"captcha provider is not configured for {source}")


class RotatingHttpClient:
    def __init__(self, proxy_manager: ProxyManager) -> None:
        self.proxy_manager = proxy_manager

    async def get_json(self, url: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = await self._request("GET", url, params=params)
        return response.json()

    async def get_text(self, url: str, *, params: dict[str, Any] | None = None) -> str:
        response = await self._request("GET", url, params=params)
        return response.text

    async def _request(self, method: str, url: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
        proxy = self.proxy_manager.next_proxy()
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        timeout = httpx.Timeout(settings.PARSER_DEFAULT_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(proxy=proxy, timeout=timeout, follow_redirects=True) as client:
            response = await client.request(method, url, params=params, headers=headers)
            response.raise_for_status()
            return response


@dataclass
class DjangoParserInfrastructure:
    http: RotatingHttpClient
    rate_limiter: AsyncRateLimiter
    captcha_service: CaptchaService

    @classmethod
    def build(cls) -> DjangoParserInfrastructure:
        proxy_manager = ProxyManager()
        return cls(
            http=RotatingHttpClient(proxy_manager),
            rate_limiter=AsyncRateLimiter(settings.PARSER_RATE_LIMIT_PER_MINUTE),
            captcha_service=CaptchaService(),
        )

    async def before_request(self, source: str) -> None:
        await self.rate_limiter.wait()
        logger.info("parser.request.allowed", extra={"source": source})

    async def cache_get(self, key: str) -> dict[str, Any] | None:
        return await sync_to_async(cache.get)(key)

    async def cache_set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        await sync_to_async(cache.set)(key, value, ttl_seconds)

    async def solve_captcha(self, source: str, challenge: dict[str, Any]) -> str:
        return await self.captcha_service.solve(source, challenge)
