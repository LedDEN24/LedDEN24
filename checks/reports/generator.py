from __future__ import annotations

from io import BytesIO

from django.conf import settings
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from checks.models import Check


class ReportGenerator:
    def render_html(self, check: Check) -> str:
        return render_to_string(
            "checks/report_pdf.html",
            {"check": check, "brand_name": settings.REPORT_BRAND_NAME},
        )

    def render_pdf(self, check: Check) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(f"{settings.REPORT_BRAND_NAME}: отчет проверки #{check.pk}", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"Адрес: {check.address}", styles["Normal"]),
            Paragraph(f"Кадастровый номер: {check.cadastral_number or '-'}", styles["Normal"]),
            Paragraph(f"ФИО: {check.full_name}", styles["Normal"]),
            Paragraph(f"Риск: {check.risk_score}/100 ({check.get_risk_level_display()})", styles["Heading2"]),
            Paragraph(check.summary or "Проверка еще не завершена.", styles["Normal"]),
            Spacer(1, 12),
            Paragraph("Подозрительные признаки", styles["Heading2"]),
        ]
        for risk in check.risks.all():
            elements.append(Paragraph(f"{risk.title}: {risk.description}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Источники", styles["Heading2"]))
        for result in check.parser_results.all():
            status = "совпадение" if result.matched else "нет совпадений"
            elements.append(Paragraph(f"{result.get_source_display()}: {status}", styles["Normal"]))
        document.build(elements)
        return buffer.getvalue()
