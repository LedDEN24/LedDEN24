from __future__ import annotations

from typing import Any

from django.conf import settings


class SearchIndexer:
    """Elasticsearch adapter used to make completed checks discoverable."""

    index_name = "property-checks"

    def __init__(self) -> None:
        self._client = None

    def index_check(self, check) -> None:  # type: ignore[no-untyped-def]
        if not settings.ELASTICSEARCH_URL:
            return
        client = self._get_client()
        client.index(index=self.index_name, id=str(check.id), document=self._document(check))

    def _get_client(self):  # type: ignore[no-untyped-def]
        if self._client is None:
            from elasticsearch import Elasticsearch

            self._client = Elasticsearch(settings.ELASTICSEARCH_URL)
        return self._client

    @staticmethod
    def _document(check) -> dict[str, Any]:  # type: ignore[no-untyped-def]
        return {
            "id": str(check.id),
            "address": check.property.address,
            "cadastral_number": check.property.cadastral_number,
            "risk_score": check.risk_score,
            "status": check.status,
            "critical_risks_count": check.critical_risks_count,
            "created_at": check.created_at.isoformat(),
        }
