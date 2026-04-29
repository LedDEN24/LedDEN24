from __future__ import annotations

import hmac
import ipaddress
import os

# Из документации ЮKassa: диапазоны IP, с которых могут приходить уведомления.
# https://yookassa.ru/developers/using-api/webhooks
YOOKASSA_IP_RANGES = [
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11/32",
    "77.75.156.35/32",
    "77.75.154.128/25",
    "2a02:5180::/32",
]


def ip_in_yookassa_ranges(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for net in YOOKASSA_IP_RANGES:
        if addr in ipaddress.ip_network(net, strict=False):
            return True
    return False


def get_client_ip(request) -> str:
    remote_addr = request.META.get("REMOTE_ADDR", "") or ""
    trusted_proxy = os.getenv("TRUST_X_FORWARDED_FOR", "0") == "1"
    if not trusted_proxy:
        return remote_addr

    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return remote_addr


def is_valid_yookassa_request(request) -> bool:
    ip = get_client_ip(request)
    if not ip or not ip_in_yookassa_ranges(ip):
        return False

    secret = os.getenv("YOOKASSA_WEBHOOK_SECRET", "").strip()
    if not secret:
        return True

    provided = request.META.get("HTTP_YOOKASSA_WEBHOOK_SECRET", "") or request.headers.get("Yookassa-Webhook-Secret", "")
    if not provided:
        return False
    return hmac.compare_digest(provided, secret)
