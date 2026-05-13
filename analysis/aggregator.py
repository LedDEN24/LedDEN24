from __future__ import annotations

from collections import defaultdict
from typing import Any


def aggregate_parser_payloads(results: list[dict[str, Any]]) -> dict[str, Any]:
    aggregated: dict[str, Any] = {
        "debts": [],
        "court_cases": [],
        "bankruptcy_records": [],
        "ads": [],
        "mentions": [],
        "fraud_matches": [],
        "encumbrances": [],
        "ownership_transitions": [],
        "source_status": {},
        "matches": [],
    }
    seen: dict[str, set[str]] = defaultdict(set)

    for result in results:
        source = result.get("source", "")
        status = result.get("status", "")
        payload = result.get("payload") or {}
        aggregated["source_status"][source] = status

        _extend_unique(aggregated["debts"], payload.get("debts", []), seen["debts"])
        _extend_unique(aggregated["court_cases"], payload.get("court_cases", []), seen["court_cases"])
        _extend_unique(
            aggregated["bankruptcy_records"],
            payload.get("bankruptcy_records", []),
            seen["bankruptcy_records"],
        )
        _extend_unique(aggregated["ads"], payload.get("ads", []), seen["ads"])
        _extend_unique(aggregated["mentions"], payload.get("mentions", []), seen["mentions"])
        _extend_unique(aggregated["fraud_matches"], payload.get("fraud_matches", []), seen["fraud_matches"])

        property_payload = payload.get("property") or {}
        _extend_unique(aggregated["encumbrances"], property_payload.get("encumbrances", []), seen["encumbrances"])
        _extend_unique(
            aggregated["ownership_transitions"],
            property_payload.get("ownership_transitions", []),
            seen["ownership_transitions"],
        )

    aggregated["matches"] = find_cross_source_matches(aggregated)
    return aggregated


def find_cross_source_matches(aggregated: dict[str, Any]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    debt_names = {item.get("debtor_name") for item in aggregated.get("debts", []) if item.get("debtor_name")}
    court_names = {item.get("party_name") for item in aggregated.get("court_cases", []) if item.get("party_name")}
    bankruptcy_names = {
        item.get("debtor_name") for item in aggregated.get("bankruptcy_records", []) if item.get("debtor_name")
    }
    for name in sorted((debt_names & court_names) | (court_names & bankruptcy_names) | (debt_names & bankruptcy_names)):
        matches.append({"type": "person_cross_source", "value": name, "sources": ["debts", "courts", "bankruptcy"]})
    return matches


def _extend_unique(target: list[dict[str, Any]], values: list[dict[str, Any]], seen: set[str]) -> None:
    for value in values:
        key = str(value.get("id") or value.get("url") or value.get("case_number") or value)
        if key in seen:
            continue
        seen.add(key)
        target.append(value)
