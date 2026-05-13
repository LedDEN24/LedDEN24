from __future__ import annotations

from rest_framework import serializers

from checks.models import Check, CourtCase, Debt, Owner, ParserResult, Property, Risk


class ParserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParserResult
        fields = (
            "id",
            "source",
            "status",
            "payload",
            "matched_fields",
            "error",
            "duration_ms",
            "fetched_at",
        )


class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = ("id", "code", "title", "description", "severity", "weight", "evidence", "created_at")


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ("id", "address", "cadastral_number", "area", "category", "market_price", "metadata")


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ("id", "full_name", "inn", "phone", "email", "source", "metadata")


class CourtCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtCase
        fields = (
            "id",
            "case_number",
            "court_name",
            "participant",
            "status",
            "claim_amount",
            "filed_at",
            "source_url",
            "metadata",
        )


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ("id", "debtor_name", "amount", "proceeding_number", "bailiff_department", "source_url", "metadata")


class CheckCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Check
        fields = ("address", "cadastral_number", "full_name", "phone", "email", "inn")

    def validate(self, attrs):
        if not any(attrs.get(field) for field in ("address", "cadastral_number", "full_name", "phone", "email", "inn")):
            raise serializers.ValidationError("Передайте хотя бы один параметр для проверки.")
        return attrs


class CheckSerializer(serializers.ModelSerializer):
    parser_results = ParserResultSerializer(many=True, read_only=True)
    risks = RiskSerializer(many=True, read_only=True)
    properties = PropertySerializer(many=True, read_only=True)
    owners = OwnerSerializer(many=True, read_only=True)
    court_cases = CourtCaseSerializer(many=True, read_only=True)
    debts = DebtSerializer(many=True, read_only=True)
    report_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Check
        fields = (
            "id",
            "address",
            "cadastral_number",
            "full_name",
            "phone",
            "email",
            "inn",
            "status",
            "risk_score",
            "error_message",
            "report_html",
            "report_pdf_url",
            "parser_results",
            "risks",
            "properties",
            "owners",
            "court_cases",
            "debts",
            "created_at",
            "updated_at",
        )

    def get_report_pdf_url(self, obj: Check) -> str:
        request = self.context.get("request")
        if not obj.report_pdf:
            return ""
        url = obj.report_pdf.url
        return request.build_absolute_uri(url) if request else url
