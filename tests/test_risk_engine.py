from __future__ import annotations

from apps.checks.models import ParserResult, Source
from apps.risk.engine import RiskEngine


def test_risk_engine_scores_only_configured_matching_records() -> None:
    result = ParserResult(
        source=Source.FSSP,
        status=ParserResult.Status.SUCCESS,
        normalized_payload={
            "configured": True,
            "matches_count": 1,
            "risk_flags": ["debts", "enforcement_proceedings"],
            "records": [{"proceeding_number": "123", "amount": "50000"}],
        },
    )
    unconfigured = ParserResult(
        source=Source.ROSREESTR,
        status=ParserResult.Status.EMPTY,
        normalized_payload={"configured": False, "risk_flags": ["arrests"], "records": []},
    )

    analysis = RiskEngine().analyse([result, unconfigured])

    assert analysis.score == 38
    assert len(analysis.findings) == 2
    assert "Высокий" in analysis.summary or "Средний" in analysis.summary
