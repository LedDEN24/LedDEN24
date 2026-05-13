from django.contrib import admin

from .models import CryptoPayment, CryptoWallet


@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ("title", "currency", "network", "is_active")
    list_filter = ("currency", "network", "is_active")
    search_fields = ("title", "address")


admin.site.register(CryptoPayment)
