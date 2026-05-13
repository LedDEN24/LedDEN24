from rest_framework import serializers

from checks.models import Check, CourtCase, Debt, Owner, ParserResult, Property, Risk


class ParserResultSerializer(serializers.ModelSerializer):
    source_display = serializers.CharField(source="get_source_display", read_only=True)

    class Meta:
        model = ParserResult
        fields = (
            "id",
            "source",
            "source_display",
            "status",
            "matched",
            "confidence",
            "payload",
            "error",
            "fetched_at",
        )
        read_only_fields = fields


class RiskSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Risk
        fields = (
            "id",
            "source",
            "level",
            "level_display",
            "score",
            "code",
            "title",
            "description",
            "evidence",
        )
        read_only_fields = fields


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "id",
            "address",
            "cadastral_number",
            "area",
            "property_type",
            "registration_status",
            "metadata",
        )
        read_only_fields = fields


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ("id", "full_name", "inn", "phone", "email", "ownership_share", "metadata")
        read_only_fields = fields


class CourtCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtCase
        fields = (
            "id",
            "source",
            "case_number",
            "court_name",
            "participant",
            "claim_amount",
            "status",
            "url",
            "metadata",
        )
        read_only_fields = fields


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ("id", "source", "debtor_name", "amount", "proceeding_number", "status", "metadata")
        read_only_fields = fields


class CheckCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Check
        fields = ("id", "address", "cadastral_number", "full_name", "phone", "email", "inn")
        read_only_fields = ("id",)


class CheckSerializer(serializers.ModelSerializer):
    parser_results = ParserResultSerializer(many=True, read_only=True)
    risks = RiskSerializer(many=True, read_only=True)
    properties = PropertySerializer(many=True, read_only=True)
    owners = OwnerSerializer(many=True, read_only=True)
    court_cases = CourtCaseSerializer(many=True, read_only=True)
    debts = DebtSerializer(many=True, read_only=True)
    risk_level_display = serializers.CharField(source="get_risk_level_display", read_only=True)

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
            "risk_level",
            "risk_level_display",
            "summary",
            "created_at",
            "started_at",
            "completed_at",
            "parser_results",
            "risks",
            "properties",
            "owners",
            "court_cases",
            "debts",
        )
        read_only_fields = (
            "status",
            "risk_score",
            "risk_level",
            "summary",
            "created_at",
            "started_at",
            "completed_at",
            "parser_results",
            "risks",
            "properties",
            "owners",
            "court_cases",
            "debts",
        )
