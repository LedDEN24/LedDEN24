from __future__ import annotations

from typing import Any, cast

from django.conf import settings
from elasticsearch import Elasticsearch

from .models import Check


class CheckSearchIndexer:
    index_name = "estate_checks"

    def __init__(self, client: Elasticsearch | None = None) -> None:
        self.client = client or Elasticsearch(settings.ELASTICSEARCH_URL)

    def index(self, check: Check) -> None:
        self.client.index(index=self.index_name, id=str(check.id), document=self.document(check))

    def search(self, query: str, *, size: int = 20) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self.client.search(
                index=self.index_name,
                size=size,
                query={
                    "multi_match": {
                        "query": query,
                        "fields": ["address", "cadastral_number", "risk_summary", "risks"],
                    }
                },
            ),
        )

    @staticmethod
    def document(check: Check) -> dict[str, Any]:
        return {
            "id": str(check.id),
            "address": check.property.address,
            "cadastral_number": check.property.cadastral_number,
            "risk_score": check.risk_score,
            "risk_summary": check.risk_summary,
            "risks": [risk.title for risk in check.risks.all()],
            "created_at": check.created_at.isoformat(),
        }
