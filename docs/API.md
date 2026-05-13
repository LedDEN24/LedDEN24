# API examples

All endpoints require JWT authentication unless explicitly exposed by the auth
router.

## Get JWT

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst","password":"password"}'
```

## Create check

```bash
curl -X POST http://localhost:8000/api/v1/checks/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "г. Москва, ул. Примерная, д. 1",
    "cadastral_number": "77:01:0000000:1001",
    "region": "Москва",
    "seller": {
      "full_name": "Иванов Иван Иванович",
      "phone": "+79990000000",
      "email": "seller@example.com",
      "inn": "770000000000"
    }
  }'
```

## Start parser orchestration

```bash
curl -X POST http://localhost:8000/api/v1/checks/<check-id>/run/ \
  -H "Authorization: Bearer <token>"
```

## Fetch risks

```bash
curl http://localhost:8000/api/v1/checks/<check-id>/risks/ \
  -H "Authorization: Bearer <token>"
```

## Download reports

```bash
curl -OJ "http://localhost:8000/api/v1/checks/<check-id>/report/?format=json" \
  -H "Authorization: Bearer <token>"

curl -OJ "http://localhost:8000/api/v1/checks/<check-id>/report/?format=pdf" \
  -H "Authorization: Bearer <token>"

curl -OJ "http://localhost:8000/api/v1/checks/<check-id>/report/?format=xlsx" \
  -H "Authorization: Bearer <token>"
```

## Parser failover strategy

Each parser is independently retried with bounded backoff. A failed source writes
a failed parser result but does not fail the entire check unless the orchestration
or persistence layer fails. The risk engine operates on partial data and the
report includes `source_status` so analysts can see coverage gaps.

## Security checklist

- Use a stable Fernet key in `FIELD_ENCRYPTION_KEY`.
- Keep OpenAI, proxy, database, and JWT secrets in the deployment secret store.
- Place users into the `analyst` group for organization-wide access; otherwise
  users can only read their own checks.
- Tune DRF throttle rates for public exposure.
- Store raw scraped files outside the relational DB and reference them through
  `raw_reference`.
