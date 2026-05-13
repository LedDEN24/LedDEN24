from rest_framework import serializers

from apps.cash_requests.models import CashMeeting
from apps.crypto_payments.models import CryptoPayment
from .models import Donation, DonationAllocation, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "provider", "provider_reference", "receipt", "screenshot", "created_at"]
        read_only_fields = ["created_at"]


class DonationAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationAllocation
        fields = ["id", "project", "amount", "allocated_by", "created_at"]
        read_only_fields = ["allocated_by", "created_at"]


class DonationSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(required=False)
    allocations = DonationAllocationSerializer(many=True, read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "reference",
            "project",
            "amount",
            "currency",
            "method",
            "status",
            "purpose",
            "comment",
            "donor_name",
            "donor_email",
            "is_anonymous",
            "suspicious_score",
            "suspicious_reason",
            "rejection_reason",
            "transaction",
            "allocations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reference", "status", "suspicious_score", "suspicious_reason", "rejection_reason", "created_at", "updated_at"]

    def create(self, validated_data):
        transaction_data = validated_data.pop("transaction", None)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["donor"] = request.user
            validated_data.setdefault("donor_email", request.user.email)
            validated_data.setdefault("donor_name", request.user.get_full_name())
        donation = Donation.objects.create(**validated_data)
        if transaction_data:
            Transaction.objects.create(donation=donation, **transaction_data)
        return donation


class DonationReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[Donation.Status.APPROVED, Donation.Status.REJECTED])
    reason = serializers.CharField(required=False, allow_blank=True)


class CryptoDonationSerializer(DonationSerializer):
    wallet_id = serializers.IntegerField(write_only=True)
    expected_crypto_amount = serializers.DecimalField(max_digits=24, decimal_places=8, write_only=True)

    class Meta(DonationSerializer.Meta):
        fields = DonationSerializer.Meta.fields + ["wallet_id", "expected_crypto_amount"]

    def create(self, validated_data):
        wallet_id = validated_data.pop("wallet_id")
        expected_crypto_amount = validated_data.pop("expected_crypto_amount")
        donation = super().create(validated_data)
        CryptoPayment.objects.create(donation=donation, wallet_id=wallet_id, expected_amount=expected_crypto_amount)
        return donation


class CashDonationSerializer(DonationSerializer):
    city = serializers.CharField(write_only=True)
    preferred_place = serializers.CharField(write_only=True)
    preferred_time = serializers.DateTimeField(write_only=True)

    class Meta(DonationSerializer.Meta):
        fields = DonationSerializer.Meta.fields + ["city", "preferred_place", "preferred_time"]

    def create(self, validated_data):
        meeting_data = {
            "city": validated_data.pop("city"),
            "preferred_place": validated_data.pop("preferred_place"),
            "preferred_time": validated_data.pop("preferred_time"),
        }
        donation = super().create(validated_data)
        CashMeeting.objects.create(donation=donation, **meeting_data)
        return donation
