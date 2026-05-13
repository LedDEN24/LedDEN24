# Estate Guard architecture

## Components

- **Django REST API** accepts real estate due-diligence requests and exposes JSON, HTML, PDF, and XLSX reports.
- **Celery workers** run parser orchestration, risk analysis, AI summaries, report side effects, and search indexing.
- **Parser manager** executes source parsers asynchronously with bounded concurrency.
- **Parser services** are isolated adapters per source: ФССП, ЕФРСБ, КАД Арбитр, суды РФ, Росреестр, кадастровая карта, tax data, enforcement databases, Avito, Cian, Domclick, open Telegram/forums, problem developers, fraud registries, and media.
- **Anti-ban layer** centralizes proxy rotation, user-agent rotation, rate limits, retries, cache, structured logging, and captcha abstraction.
- **Risk engine** merges normalized parser data, finds matches, computes risk score, and emits explainable risk findings.
- **AI analyzer** enriches findings with plain-language summaries and legal recommendations. It falls back to deterministic text when no OpenAI key is configured.
- **Elasticsearch** indexes checks for operational search.
- **Prometheus/Grafana/Flower** provide metrics and Celery monitoring.

## Parser flow

1. API creates `Check`, `Property`, and encrypted `Owner` records.
2. `run_property_check` Celery task builds `ParserContext`.
3. `ParserManager.run_all` starts parser services concurrently.
4. Each parser receives rotating headers/proxy, respects rate limits, retries transient failures, and uses cache.
5. Raw and normalized payloads are stored as `ParserResult`.
6. Domain records (`Debt`, `CourtCase`, `BankruptcyRecord`, `ScrapedAd`) are materialized from normalized records.
7. `RiskEngine` computes findings and score.
8. `AiRiskAnalyzer` creates final explanation and recommendations.
9. Check is indexed in Elasticsearch and reports become available from the API.

## Failover strategy

- Parser failures are isolated per source and stored as failed parser results.
- HTTP 429/403/5xx use exponential backoff and anti-ban telemetry.
- Captcha detection returns `captcha_required` unless a concrete solver is configured.
- Search indexing and AI failures are non-critical and do not block check completion.
- Celery retries task-level transient timeouts with backoff.

## Security

- JWT authentication is enabled by default.
- RBAC uses Django groups: `analyst`, `manager`, and `admin`.
- API throttling is configured for anonymous users, authenticated users, checks, and reports.
- PII fields for owners are encrypted at rest with Fernet.
- Audit logs record check creation, parser runs, risk analysis, report generation, and API access events.
- Secrets are read from environment variables and `.env` is not committed.
