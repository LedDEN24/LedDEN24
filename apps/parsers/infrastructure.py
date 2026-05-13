from __future__ import annotations

import asyncio
import logging
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self, proxies: list[str] | None = None) -> None:
        self._proxies = deque(proxies or getattr(settings, "PARSER_PROXIES", []))

    def next_proxy(self) -> str | None:
        if not self._proxies:
            return None
        proxy = self._proxies[0]
        self._proxies.rotate(-1)
        return proxy

    def report_failure(self, proxy: str | None) -> None:
        if proxy:
            logger.warning("proxy_failure", extra={"proxy": proxy})


class UserAgentRotator:
    def __init__(self, user_agents: list[str] | None = None) -> None:
        self.user_agents = user_agents or getattr(settings, "PARSER_USER_AGENTS", [])

    def next(self) -> str:
        return random.choice(self.user_agents) if self.user_agents else "EstateGuardBot/0.1"


class AsyncRateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def acquire(self, key: str) -> None:
        async with self._lock:
            now = time.monotonic()
            window = self._hits[key]
            while window and now - window[0] > 60:
                window.popleft()
            if len(window) >= self.per_minute:
                sleep_for = 60 - (now - window[0])
                await asyncio.sleep(max(sleep_for, 0))
            window.append(time.monotonic())


class ParserCache:
    def __init__(self, ttl_seconds: int | None = None) -> None:
        self.ttl_seconds = ttl_seconds or getattr(settings, "PARSER_CACHE_TTL_SECONDS", 3600)

    def get(self, key: str) -> dict[str, Any] | None:
        return cache.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        cache.set(key, value, self.ttl_seconds)


class CaptchaService:
    async def solve(self, image_or_site_key: str, *, source: str) -> str | None:
        logger.info("captcha_solver_not_configured", extra={"source": source})
        return None


@dataclass
class AntiBanDependency:
    proxy_manager: ProxyManager
    user_agent_rotator: UserAgentRotator
    rate_limiter: AsyncRateLimiter

    async def before_request(self, source: str) -> dict[str, Any]:
        await self.rate_limiter.acquire(source)
        proxy = self.proxy_manager.next_proxy()
        return {
            "proxy": proxy,
            "headers": {
                "User-Agent": self.user_agent_rotator.next(),
                "Accept": "text/html,application/xhtml+xml,application/json",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            },
        }

    async def after_response(self, source: str, response, error: Exception | None) -> None:  # type: ignore[no-untyped-def]
        if error:
            logger.info("parser_request_error", extra={"source": source, "error": str(error)})
        if response is not None and response.status_code in {403, 429, 503}:
            logger.warning(
                "parser_antiban_signal",
                extra={"source": source, "status_code": response.status_code},
            )


def build_default_dependency() -> AntiBanDependency:
    return AntiBanDependency(
        proxy_manager=ProxyManager(),
        user_agent_rotator=UserAgentRotator(),
        rate_limiter=AsyncRateLimiter(getattr(settings, "PARSER_RATE_LIMIT_PER_MINUTE", 30)),
    )
