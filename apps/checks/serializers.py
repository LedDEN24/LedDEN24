from __future__ import annotations

from rest_framework import serializers

from apps.checks.models import (
    BankruptcyRecord,
    Check,
    CourtCase,
    Debt,
    Owner,
    ParserResult,
    Property,
    Risk,
    ScrapedAd,
)


class OwnerInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=512)
    phone = serializers.CharField(max_length=64, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    inn = serializers.CharField(max_length=32, required=False, allow_blank=True)


class PropertyCheckCreateSerializer(serializers.Serializer):
    address = serializers.CharField()
    cadastral_number = serializers.CharField(max_length=64)
    region = serializers.CharField(max_length=128, required=False, allow_blank=True)
    seller = OwnerInputSerializer()


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ["id", "address", "cadastral_number", "region", "metadata", "created_at"]


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ["id", "full_name", "phone", "email", "inn", "metadata"]


class ParserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParserResult
        fields = ["id", "source", "status", "payload", "error", "duration_ms", "created_at"]


class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = [
            "id",
            "code",
            "title",
            "severity",
            "score_impact",
            "explanation",
            "evidence",
            "recommendations",
        ]


class CourtCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtCase
        fields = "__all__"


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = "__all__"


class BankruptcyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankruptcyRecord
        fields = "__all__"


class ScrapedAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedAd
        fields = "__all__"


class CheckSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    risks = RiskSerializer(many=True, read_only=True)
    parser_results = ParserResultSerializer(many=True, read_only=True)

    class Meta:
        model = Check
        fields = [
            "id",
            "property",
            "status",
            "risk_score",
            "critical_risks_count",
            "started_at",
            "completed_at",
            "error",
            "ai_summary",
            "aggregated_data",
            "risks",
            "parser_results",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
