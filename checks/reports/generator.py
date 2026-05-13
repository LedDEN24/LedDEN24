from __future__ import annotations

from io import BytesIO

from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from checks.models import Check


class ReportGenerator:
    def generate(self, check: Check) -> Check:
        check.refresh_from_db()
        context = {
            "check": check,
            "parser_results": check.parser_results.all(),
            "risks": check.risks.all(),
            "properties": check.properties.all(),
            "owners": check.owners.all(),
            "court_cases": check.court_cases.all(),
            "debts": check.debts.all(),
        }
        html = render_to_string("checks/report_pdf.html", context)
        pdf_bytes = self._build_pdf(check, html)
        check.report_html = html
        check.report_pdf.save(f"check-{check.pk}.pdf", ContentFile(pdf_bytes), save=False)
        check.save(update_fields=("report_html", "report_pdf", "updated_at"))
        return check

    @staticmethod
    def _build_pdf(check: Check, html: str) -> bytes:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 48
        lines = [
            f"Отчет по проверке #{check.pk}",
            f"Адрес: {check.address}",
            f"Кадастровый номер: {check.cadastral_number or '-'}",
            f"ФИО: {check.full_name or '-'}",
            f"ИНН: {check.inn or '-'}",
            f"Risk score: {check.risk_score}/100",
            "",
            "Ключевые риски:",
        ]
        for risk in check.risks.all()[:20]:
            lines.append(f"- {risk.title} [{risk.severity}] +{risk.weight}")
        if not check.risks.exists():
            lines.append("- Существенные риски не выявлены")

        pdf.setFont("Helvetica", 11)
        for line in lines:
            if y < 48:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y = height - 48
            pdf.drawString(48, y, line[:110])
            y -= 18
        pdf.showPage()
        pdf.save()
        return buffer.getvalue()
