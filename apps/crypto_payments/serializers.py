from rest_framework import serializers

from .models import CryptoPayment, CryptoWallet


class CryptoWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoWallet
        fields = ["id", "currency", "network", "address", "label", "is_active", "min_confirmations", "created_at"]
        read_only_fields = ["id", "created_at"]


class CryptoPaymentSerializer(serializers.ModelSerializer):
    wallet_address = serializers.CharField(source="wallet.address", read_only=True)

    class Meta:
        model = CryptoPayment
        fields = ["id", "donation", "wallet", "wallet_address", "tx_hash", "network", "expected_amount", "received_amount", "confirmations", "status", "expires_at", "created_at", "updated_at"]
        read_only_fields = ["id", "wallet_address", "created_at", "updated_at"]
