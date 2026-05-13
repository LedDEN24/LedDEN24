from __future__ import annotations

import abc
import asyncio
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class ParserStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ParserInput:
    check_id: str
    address: str
    cadastral_number: str
    seller_full_name: str
    phone: str = ""
    email: str = ""
    inn: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParserOutput:
    source: str
    status: ParserStatus
    payload: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    duration_ms: int = 0
    raw_reference: str = ""


class AsyncHttpClient(Protocol):
    async def get_json(self, url: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        ...

    async def get_text(self, url: str, *, params: dict[str, Any] | None = None) -> str:
        ...


class ParserInfrastructure(Protocol):
    http: AsyncHttpClient

    async def before_request(self, source: str) -> None:
        ...

    async def cache_get(self, key: str) -> dict[str, Any] | None:
        ...

    async def cache_set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        ...

    async def solve_captcha(self, source: str, challenge: dict[str, Any]) -> str:
        ...


class BaseParser(abc.ABC):
    source: str
    ttl_seconds = 60 * 60 * 24
    max_attempts = 3
    retry_backoff_seconds = 1.5

    def __init__(self, infrastructure: ParserInfrastructure) -> None:
        self.infrastructure = infrastructure

    async def run(self, parser_input: ParserInput) -> ParserOutput:
        started = time.perf_counter()
        cache_key = self.cache_key(parser_input)
        cached = await self.infrastructure.cache_get(cache_key)
        if cached is not None:
            return ParserOutput(
                source=self.source,
                status=ParserStatus.SUCCESS,
                payload={**cached, "_cache_hit": True},
                duration_ms=self._duration_ms(started),
            )

        last_error = ""
        for attempt in range(1, self.max_attempts + 1):
            try:
                await self.infrastructure.before_request(self.source)
                payload = await self.parse(parser_input)
                await self.infrastructure.cache_set(cache_key, payload, self.ttl_seconds)
                return ParserOutput(
                    source=self.source,
                    status=ParserStatus.SUCCESS,
                    payload=payload,
                    duration_ms=self._duration_ms(started),
                )
            except CaptchaRequired as exc:
                token = await self.infrastructure.solve_captcha(self.source, exc.challenge)
                try:
                    payload = await self.parse(parser_input, captcha_token=token)
                    await self.infrastructure.cache_set(cache_key, payload, self.ttl_seconds)
                    return ParserOutput(
                        source=self.source,
                        status=ParserStatus.SUCCESS,
                        payload=payload,
                        duration_ms=self._duration_ms(started),
                    )
                except Exception as nested_exc:  # noqa: BLE001
                    last_error = f"captcha retry failed: {nested_exc}"
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)

            if attempt < self.max_attempts:
                await asyncio.sleep(self.retry_backoff_seconds * attempt)

        return ParserOutput(
            source=self.source,
            status=ParserStatus.FAILED,
            error=last_error,
            duration_ms=self._duration_ms(started),
        )

    @abc.abstractmethod
    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        raise NotImplementedError

    def cache_key(self, parser_input: ParserInput) -> str:
        return f"parser:{self.source}:{parser_input.cadastral_number}:{parser_input.inn}:{parser_input.seller_full_name.casefold()}"

    @staticmethod
    def _duration_ms(started: float) -> int:
        return int((time.perf_counter() - started) * 1000)


class CaptchaRequired(RuntimeError):
    def __init__(self, challenge: dict[str, Any]) -> None:
        super().__init__("captcha required")
        self.challenge = challenge
