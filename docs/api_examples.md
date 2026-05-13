# API examples

## Obtain JWT

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst@example.com","password":"password"}'
```

## Start a property check

```bash
curl -X POST http://localhost:8000/api/checks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Москва, ул. Примерная, д. 1",
    "cadastral_number": "77:01:0004010:1234",
    "seller_full_name": "Иванов Иван Иванович",
    "seller_phone": "+79990000000",
    "seller_email": "seller@example.com",
    "seller_inn": "770000000000",
    "region": "Москва"
  }'
```

The response is `202 Accepted`; parsing continues in Celery.

## Get check status and JSON report

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/checks/$CHECK_ID/

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/checks/$CHECK_ID/report/?format=json"
```

## Download HTML/PDF/XLSX

```bash
curl -L -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/checks/$CHECK_ID/report/?format=html" \
  -o report.html

curl -L -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/checks/$CHECK_ID/report/?format=pdf" \
  -o report.pdf

curl -L -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/checks/$CHECK_ID/report/?format=xlsx" \
  -o report.xlsx
```
