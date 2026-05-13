from rest_framework import serializers

from .models import CryptoPayment, CryptoWallet


class CryptoWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoWallet
        fields = ["id", "title", "network", "currency", "address", "qr_code", "is_active"]


class CryptoPaymentSerializer(serializers.ModelSerializer):
    wallet = CryptoWalletSerializer(read_only=True)

    class Meta:
        model = CryptoPayment
        fields = ["id", "donation", "wallet", "tx_hash", "expected_amount", "received_amount", "confirmations", "status", "created_at"]
        read_only_fields = ["created_at"]
