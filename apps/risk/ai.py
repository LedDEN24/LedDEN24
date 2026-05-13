from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AiRiskConclusion:
    summary: str
    legal_recommendations: list[str]
    final_conclusion: str


class AiRiskAnalyzer:
    system_prompt = (
        "Ты юридический аналитик по сделкам с недвижимостью РФ. "
        "Объясняй риски простым языком, не выдумывай факты, указывай что требует ручной проверки."
    )

    def analyse(self, risk_payload: dict[str, Any]) -> AiRiskConclusion:
        if not getattr(settings, "OPENAI_API_KEY", ""):
            return self._fallback(risk_payload)
        try:
            return self._call_openai(risk_payload)
        except Exception:  # noqa: BLE001 - AI must not block report generation.
            logger.exception("ai_risk_analysis_failed")
            return self._fallback(risk_payload)

    def _call_openai(self, risk_payload: dict[str, Any]) -> AiRiskConclusion:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Верни JSON с ключами summary, legal_recommendations, final_conclusion. "
                        f"Данные риска: {json.dumps(risk_payload, ensure_ascii=False)}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return AiRiskConclusion(
            summary=str(data.get("summary", "")),
            legal_recommendations=list(data.get("legal_recommendations", [])),
            final_conclusion=str(data.get("final_conclusion", "")),
        )

    @staticmethod
    def _fallback(risk_payload: dict[str, Any]) -> AiRiskConclusion:
        score = risk_payload.get("score", 0)
        findings = risk_payload.get("findings", [])
        if score >= 70:
            conclusion = "Сделка имеет высокий риск. Рекомендуется приостановить подписание до проверки юристом."
        elif score >= 35:
            conclusion = "Сделка требует расширенной юридической проверки и подтверждающих документов."
        else:
            conclusion = "Критичные признаки не выявлены, но документы необходимо сверить вручную."
        return AiRiskConclusion(
            summary=f"Автоматический анализ выявил {len(findings)} риск-факторов. Risk score: {score}/100.",
            legal_recommendations=[
                "Запросить свежую выписку ЕГРН и проверить обременения.",
                "Сверить паспортные данные продавца и полномочия на сделку.",
                "Проверить историю переходов права и основания собственности.",
                "При наличии долгов, судов или банкротства получить письменное заключение юриста.",
            ],
            final_conclusion=conclusion,
        )
