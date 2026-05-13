from __future__ import annotations

import io
import json
from enum import StrEnum
from typing import Any

import pandas as pd
from django.template.loader import render_to_string


class ReportFormat(StrEnum):
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    XLSX = "xlsx"


class ReportService:
    def render(self, check, report_format: ReportFormat) -> tuple[bytes | str, str, str]:  # type: ignore[no-untyped-def]
        data = self.build_payload(check)
        if report_format == ReportFormat.JSON:
            return (
                json.dumps(data, ensure_ascii=False, indent=2),
                "application/json; charset=utf-8",
                f"check-{check.id}.json",
            )
        if report_format == ReportFormat.HTML:
            html = self.render_html(data)
            return html, "text/html; charset=utf-8", f"check-{check.id}.html"
        if report_format == ReportFormat.PDF:
            return self.render_pdf(data), "application/pdf", f"check-{check.id}.pdf"
        if report_format == ReportFormat.XLSX:
            return self.render_xlsx(data), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"check-{check.id}.xlsx"
        raise ValueError(f"Unsupported report format: {report_format}")

    def build_payload(self, check) -> dict[str, Any]:  # type: ignore[no-untyped-def]
        risks = list(check.risks.order_by("-score_impact").values())
        return {
            "check": {
                "id": str(check.id),
                "status": check.status,
                "risk_score": check.risk_score,
                "critical_risks_count": check.critical_risks_count,
                "created_at": check.created_at.isoformat(),
                "completed_at": check.completed_at.isoformat() if check.completed_at else None,
            },
            "property": {
                "address": check.property.address,
                "cadastral_number": check.property.cadastral_number,
                "region": check.property.region,
            },
            "critical_risks": [risk for risk in risks if risk["severity"] == "critical"],
            "risks": risks,
            "timeline": self._timeline(check),
            "matches": check.aggregated_data.get("matches", []),
            "court_cases": list(check.court_cases.values()),
            "debts": list(check.debts.values()),
            "bankruptcy_records": list(check.bankruptcy_records.values()),
            "scraped_ads": list(check.scraped_ads.values()),
            "ai_summary": check.ai_summary,
            "recommendations": self._recommendations(risks, check.ai_summary),
        }

    def render_html(self, data: dict[str, Any]) -> str:
        return render_to_string("reports/property_check.html", {"report": data})

    def render_pdf(self, data: dict[str, Any]) -> bytes:
        html = self.render_html(data)
        try:
            from weasyprint import HTML

            return HTML(string=html).write_pdf()
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("PDF backend is unavailable") from exc

    def render_xlsx(self, data: dict[str, Any]) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame([data["check"]]).to_excel(writer, sheet_name="summary", index=False)
            pd.DataFrame(data["risks"]).to_excel(writer, sheet_name="risks", index=False)
            pd.DataFrame(data["court_cases"]).to_excel(writer, sheet_name="court_cases", index=False)
            pd.DataFrame(data["debts"]).to_excel(writer, sheet_name="debts", index=False)
            pd.DataFrame(data["bankruptcy_records"]).to_excel(writer, sheet_name="bankruptcy", index=False)
            pd.DataFrame(data["scraped_ads"]).to_excel(writer, sheet_name="ads", index=False)
        return output.getvalue()

    @staticmethod
    def _timeline(check) -> list[dict[str, Any]]:  # type: ignore[no-untyped-def]
        events: list[dict[str, Any]] = [
            {"at": check.created_at.isoformat(), "type": "check_created", "title": "Проверка создана"}
        ]
        for result in check.parser_results.order_by("created_at"):
            events.append(
                {
                    "at": result.created_at.isoformat(),
                    "type": "parser_result",
                    "title": f"{result.source}: {result.status}",
                }
            )
        if check.completed_at:
            events.append({"at": check.completed_at.isoformat(), "type": "check_completed", "title": "Проверка завершена"})
        return events

    @staticmethod
    def _recommendations(risks: list[dict[str, Any]], ai_summary: dict[str, Any]) -> list[str]:
        recommendations: list[str] = []
        for risk in risks:
            recommendations.extend(risk.get("recommendations") or [])
        recommendations.extend(ai_summary.get("recommendations") or [])
        return list(dict.fromkeys(recommendations))
