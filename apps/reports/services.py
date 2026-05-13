from __future__ import annotations

import json
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import pandas as pd
from django.template.loader import render_to_string
from weasyprint import HTML

from apps.checks.models import Check


class ReportFormat:
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    XLSX = "xlsx"


@dataclass(frozen=True)
class ReportService:
    def render(self, check: Check, fmt: str) -> tuple[bytes | str | dict[str, Any], str, str]:
        data = self.as_dict(check)
        if fmt == ReportFormat.HTML:
            html = render_to_string("reports/check_report.html", {"report": data})
            return html, "text/html; charset=utf-8", f"check-{check.id}.html"
        if fmt == ReportFormat.PDF:
            html = render_to_string("reports/check_report.html", {"report": data})
            return HTML(string=html).write_pdf(), "application/pdf", f"check-{check.id}.pdf"
        if fmt == ReportFormat.XLSX:
            return self._xlsx(data), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"check-{check.id}.xlsx"
        return data, "application/json", f"check-{check.id}.json"

    def as_json(self, check: Check) -> str:
        return json.dumps(self.as_dict(check), ensure_ascii=False, indent=2, default=str)

    def as_dict(self, check: Check) -> dict[str, Any]:
        return {
            "id": str(check.id),
            "status": check.status,
            "created_at": check.created_at,
            "finished_at": check.finished_at,
            "risk_score": check.risk_score,
            "risk_summary": check.risk_summary,
            "ai_summary": check.ai_summary,
            "legal_recommendations": check.legal_recommendations,
            "property": {
                "address": check.property.address,
                "cadastral_number": check.property.cadastral_number,
                "region": check.property.region,
            },
            "critical_risks": [
                self._risk_dict(risk)
                for risk in check.risks.all()
                if risk.severity == "critical"
            ],
            "risks": [self._risk_dict(risk) for risk in check.risks.all()],
            "timeline": self._timeline(check),
            "matches": [result.normalized_payload for result in check.parser_results.all()],
            "court_cases": [case.payload | {"case_number": case.case_number} for case in check.court_cases.all()],
            "debts": [debt.payload | {"amount": debt.amount} for debt in check.debts.all()],
            "bankruptcy_records": [
                record.payload | {"case_number": record.case_number}
                for record in check.bankruptcy_records.all()
            ],
            "scraped_ads": [ad.payload | {"url": ad.url, "price": ad.price} for ad in check.scraped_ads.all()],
        }

    @staticmethod
    def _risk_dict(risk) -> dict[str, Any]:  # type: ignore[no-untyped-def]
        return {
            "source": risk.source,
            "category": risk.category,
            "severity": risk.severity,
            "score": risk.score,
            "title": risk.title,
            "description": risk.description,
            "evidence": risk.evidence,
        }

    @staticmethod
    def _timeline(check: Check) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for case in check.court_cases.all():
            if case.filed_at:
                events.append({"date": case.filed_at, "source": case.source, "title": case.case_number})
        for record in check.bankruptcy_records.all():
            if record.published_at:
                events.append({"date": record.published_at, "source": record.source, "title": record.case_number})
        return sorted(events, key=lambda item: item["date"])

    @staticmethod
    def _xlsx(data: dict[str, Any]) -> bytes:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame([data["property"]]).to_excel(writer, sheet_name="property", index=False)
            pd.DataFrame(data["risks"]).to_excel(writer, sheet_name="risks", index=False)
            pd.DataFrame(data["court_cases"]).to_excel(writer, sheet_name="court_cases", index=False)
            pd.DataFrame(data["debts"]).to_excel(writer, sheet_name="debts", index=False)
            pd.DataFrame(data["bankruptcy_records"]).to_excel(writer, sheet_name="bankruptcy", index=False)
            pd.DataFrame(data["scraped_ads"]).to_excel(writer, sheet_name="ads", index=False)
        return output.getvalue()
