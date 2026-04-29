# Nginx pack for YooKassa webhook

Внутри 2 готовых варианта location-блока:

- `nginx/yookassa_webhook_variant1.conf` — IP allowlist в Nginx, без BasicAuth.
- `nginx/yookassa_webhook_variant3.conf` — IP allowlist в Nginx + Nginx добавляет `Authorization: Basic ...` при проксировании в Django.

## Быстрая установка (Variant 1)
1) Скопируй содержимое `nginx/yookassa_webhook_variant1.conf` в твой `server { ... }`
2) Проверь:
   - Django слушает `127.0.0.1:8000` (или поменяй `proxy_pass`)
3) Применить:
   sudo nginx -t && sudo systemctl reload nginx

## Variant 3 (рекомендуется, если хочешь BasicAuth в Django)
1) Сгенерируй base64:
   printf "webhookuser:secret" | base64
2) Вставь результат в `proxy_set_header Authorization "Basic ...";`
3) В `.env` Django выставь:
   YOOKASSA_WEBHOOK_USER=webhookuser
   YOOKASSA_WEBHOOK_PASS=secret

## Webhook URL в YooKassa
https://<твой-домен>/payments/yookassa/webhook/

## Примечания
- Если Django за Nginx, реальный IP придёт в Django через `X-Forwarded-For`.
- В проекте уже есть логирование вебхуков (WebhookLog) + проверка IP в Django (можно оставить как дополнительную защиту).
