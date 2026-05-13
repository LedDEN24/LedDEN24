from __future__ import annotations

import json
from typing import Any

import httpx
from django.conf import settings


class AiRiskAnalyzer:
    """OpenAI-compatible summarizer. Failures are non-blocking for deterministic scoring."""

    endpoint = "https://api.openai.com/v1/chat/completions"

    async def analyze(self, *, risk_score: int, findings: list[dict[str, Any]], aggregated: dict[str, Any]) -> dict[str, Any]:
        if not settings.OPENAI_API_KEY:
            return self._fallback(risk_score, findings)

        prompt = {
            "risk_score": risk_score,
            "findings": findings,
            "aggregated": {
                "source_status": aggregated.get("source_status", {}),
                "matches": aggregated.get("matches", []),
                "critical_counts": {
                    "debts": len(aggregated.get("debts", [])),
                    "court_cases": len(aggregated.get("court_cases", [])),
                    "bankruptcy_records": len(aggregated.get("bankruptcy_records", [])),
                    "encumbrances": len(aggregated.get("encumbrances", [])),
                },
            },
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": settings.OPENAI_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Ты юридический риск-аналитик недвижимости. "
                                    "Верни JSON с summary, plain_language, recommendations, final_conclusion."
                                ),
                            },
                            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001
            fallback = self._fallback(risk_score, findings)
            fallback["llm_error"] = str(exc)
            return fallback

    @staticmethod
    def _fallback(risk_score: int, findings: list[dict[str, Any]]) -> dict[str, Any]:
        critical = [item["title"] for item in findings if item.get("severity") == "critical"]
        return {
            "summary": f"Расчетный риск сделки: {risk_score}/100.",
            "plain_language": "Проверка завершена по доступным источникам. Изучите найденные риски до сделки.",
            "recommendations": [
                "Запросить свежую выписку ЕГРН",
                "Сверить паспортные и контактные данные продавца",
                "Проводить расчеты через безопасный механизм",
            ],
            "final_conclusion": "Требуется ручная юридическая проверка критичных фактов." if critical else "Критичные признаки не выявлены.",
        }
