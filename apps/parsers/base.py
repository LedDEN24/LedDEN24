from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx
from bs4 import BeautifulSoup

from apps.checks.models import ParserResult, Source

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ParserContext:
    check_id: str
    address: str
    cadastral_number: str
    seller_full_name: str
    seller_phone: str = ""
    seller_email: str = ""
    seller_inn: str = ""
    region: str = ""


@dataclass
class ParserResultDTO:
    source: str
    status: str
    raw_payload: dict[str, Any] = field(default_factory=dict)
    normalized_payload: dict[str, Any] = field(default_factory=dict)
    evidence_url: str = ""
    error: str = ""
    duration_ms: int = 0


class CaptchaSolver(Protocol):
    async def solve(self, image_or_site_key: str, *, source: str) -> str | None:
        ...


class ParserDependency(Protocol):
    async def before_request(self, source: str) -> dict[str, Any]:
        ...

    async def after_response(self, source: str, response: httpx.Response | None, error: Exception | None) -> None:
        ...


class BaseParser:
    source: Source
    endpoint_url: str = ""
    timeout_seconds = 20
    max_attempts = 3
    retry_statuses = {403, 408, 409, 425, 429, 500, 502, 503, 504}

    def __init__(
        self,
        dependency: ParserDependency,
        captcha_solver: CaptchaSolver,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.dependency = dependency
        self.captcha_solver = captcha_solver
        self.client = client

    async def execute(self, context: ParserContext) -> ParserResultDTO:
        started = time.perf_counter()
        try:
            raw = await self.parse(context)
            status = ParserResult.Status.SUCCESS if raw else ParserResult.Status.EMPTY
            normalized = self.normalize(raw)
            return ParserResultDTO(
                source=self.source,
                status=status,
                raw_payload=raw,
                normalized_payload=normalized,
                evidence_url=raw.get("evidence_url", "") if isinstance(raw, dict) else "",
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        except CaptchaRequired as exc:
            logger.warning("captcha_required", extra={"source": self.source, "error": str(exc)})
            return ParserResultDTO(
                source=self.source,
                status=ParserResult.Status.CAPTCHA_REQUIRED,
                error=str(exc),
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        except RateLimited as exc:
            logger.warning("parser_rate_limited", extra={"source": self.source, "error": str(exc)})
            return ParserResultDTO(
                source=self.source,
                status=ParserResult.Status.RATE_LIMITED,
                error=str(exc),
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        except Exception as exc:  # noqa: BLE001 - parser isolation must not break orchestration.
            logger.exception("parser_failed", extra={"source": self.source})
            return ParserResultDTO(
                source=self.source,
                status=ParserResult.Status.FAILED,
                error=str(exc),
                duration_ms=int((time.perf_counter() - started) * 1000),
            )

    async def parse(self, context: ParserContext) -> dict[str, Any]:
        if not self.endpoint_url:
            return {
                "configured": False,
                "message": "Parser endpoint is not configured; provide a legal source adapter URL.",
            }
        return await self.fetch_json(context)

    async def fetch_json(self, context: ParserContext) -> dict[str, Any]:
        response = await self._request("GET", self.endpoint_url, params=self.query_params(context))
        return response.json()

    async def fetch_html(self, context: ParserContext) -> BeautifulSoup:
        response = await self._request("GET", self.endpoint_url, params=self.query_params(context))
        return BeautifulSoup(response.text, "lxml")

    def query_params(self, context: ParserContext) -> dict[str, str]:
        return {
            "address": context.address,
            "cadastral_number": context.cadastral_number,
            "name": context.seller_full_name,
            "inn": context.seller_inn,
        }

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload

    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        attempt = 0
        last_error: Exception | None = None
        while attempt < self.max_attempts:
            attempt += 1
            response: httpx.Response | None = None
            hints = await self.dependency.before_request(self.source)
            headers = kwargs.pop("headers", {})
            headers.update(hints.get("headers", {}))
            request_kwargs = {**kwargs, "headers": headers, "timeout": self.timeout_seconds}
            proxy = hints.get("proxy")
            try:
                if self.client:
                    response = await self.client.request(method, url, **request_kwargs)
                else:
                    async with httpx.AsyncClient(follow_redirects=True, proxy=proxy) as client:
                        response = await client.request(method, url, **request_kwargs)
                await self.dependency.after_response(self.source, response, None)
                if self._looks_like_captcha(response):
                    token = await self.captcha_solver.solve(response.text[:2048], source=self.source)
                    if not token:
                        raise CaptchaRequired("captcha detected and no solver token returned")
                if response.status_code == 429:
                    raise RateLimited("source returned HTTP 429")
                if response.status_code in self.retry_statuses:
                    await asyncio.sleep(min(2**attempt, 10))
                    continue
                response.raise_for_status()
                return response
            except Exception as exc:  # noqa: BLE001 - retry layer captures transport/parser failures.
                last_error = exc
                await self.dependency.after_response(self.source, response, exc)
                if attempt >= self.max_attempts:
                    break
                await asyncio.sleep(min(2**attempt, 10))
        if last_error:
            raise last_error
        raise RuntimeError("request failed without response or exception")

    @staticmethod
    def _looks_like_captcha(response: httpx.Response) -> bool:
        text = response.text.lower()[:4096]
        return response.status_code == 403 and any(marker in text for marker in ("captcha", "капча", "recaptcha"))


class CaptchaRequired(RuntimeError):
    pass


class RateLimited(RuntimeError):
    pass
