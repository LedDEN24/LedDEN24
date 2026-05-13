from django.contrib import admin

from .models import CryptoPayment, CryptoWallet


@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ("currency", "network", "address", "is_active", "min_confirmations")
    list_filter = ("currency", "network", "is_active")
    search_fields = ("address", "label")


@admin.register(CryptoPayment)
class CryptoPaymentAdmin(admin.ModelAdmin):
    list_display = ("donation", "wallet", "status", "expected_amount", "received_amount", "confirmations", "created_at")
    list_filter = ("status", "network")
    search_fields = ("donation__public_id", "tx_hash", "wallet__address")
