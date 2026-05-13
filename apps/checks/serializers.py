from __future__ import annotations

from django.db import transaction
from rest_framework import serializers

from .models import (
    BankruptcyRecord,
    Check,
    CourtCase,
    Debt,
    ParserResult,
    Property,
    Risk,
    ScrapedAd,
)
from .normalization import normalize_text, stable_hash


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "id",
            "address",
            "normalized_address",
            "cadastral_number",
            "region",
            "property_type",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "normalized_address", "created_at", "updated_at"]


class ParserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParserResult
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CourtCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtCase
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class BankruptcyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankruptcyRecord
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ScrapedAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedAd
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CheckCreateSerializer(serializers.Serializer):
    address = serializers.CharField()
    cadastral_number = serializers.CharField(max_length=64)
    seller_full_name = serializers.CharField()
    seller_phone = serializers.CharField(required=False, allow_blank=True)
    seller_email = serializers.EmailField(required=False, allow_blank=True)
    seller_inn = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)

    @transaction.atomic
    def create(self, validated_data: dict[str, str]) -> Check:
        request = self.context.get("request")
        prop = Property.objects.create(
            address=validated_data["address"],
            normalized_address=normalize_text(validated_data["address"]),
            cadastral_number=validated_data["cadastral_number"],
            region=validated_data.get("region", ""),
        )
        owner = prop_owner_model().objects.create(
            full_name=validated_data["seller_full_name"],
            phone=validated_data.get("seller_phone", ""),
            email=validated_data.get("seller_email", ""),
            inn=validated_data.get("seller_inn", ""),
            normalized_full_name=normalize_text(validated_data["seller_full_name"]),
            inn_hash=stable_hash(validated_data.get("seller_inn", "")),
        )
        user = getattr(request, "user", None) if request else None
        return Check.objects.create(
            requested_by=user if getattr(user, "is_authenticated", False) else None,
            property=prop,
            owner=owner,
            request_payload=validated_data,
        )


def prop_owner_model():
    from .models import Owner

    return Owner


class CheckDetailSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    parser_results = ParserResultSerializer(many=True, read_only=True)
    risks = RiskSerializer(many=True, read_only=True)
    court_cases = CourtCaseSerializer(many=True, read_only=True)
    debts = DebtSerializer(many=True, read_only=True)
    bankruptcy_records = BankruptcyRecordSerializer(many=True, read_only=True)
    scraped_ads = ScrapedAdSerializer(many=True, read_only=True)

    class Meta:
        model = Check
        fields = [
            "id",
            "status",
            "risk_score",
            "risk_summary",
            "ai_summary",
            "legal_recommendations",
            "started_at",
            "finished_at",
            "error_message",
            "property",
            "parser_results",
            "risks",
            "court_cases",
            "debts",
            "bankruptcy_records",
            "scraped_ads",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
