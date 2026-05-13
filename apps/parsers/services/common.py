from __future__ import annotations

from typing import Any

from apps.parsers.base import BaseParser, ParserContext


class ConfigurableSourceParser(BaseParser):
    risk_flags: tuple[str, ...] = ()

    async def parse(self, context: ParserContext) -> dict[str, Any]:
        payload = await super().parse(context)
        payload.setdefault("query", self.query_params(context))
        payload.setdefault("risk_flags", list(self.risk_flags))
        payload.setdefault("matches", [])
        return payload

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "configured": payload.get("configured", True),
            "matches_count": len(payload.get("matches", [])),
            "risk_flags": payload.get("risk_flags", []),
            "records": payload.get("records", payload.get("matches", [])),
            "evidence_url": payload.get("evidence_url", ""),
        }
