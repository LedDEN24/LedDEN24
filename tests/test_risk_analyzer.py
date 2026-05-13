from checks.models import ParserSource, RiskLevel
from checks.services.risk_analyzer import RiskAnalyzer


def test_risk_analyzer_scores_structured_debts():
    results = [
        {
            "source": ParserSource.FSSP.value,
            "matched": True,
            "confidence": 1,
            "payload": {
                "debts": [
                    {
                        "debtor_name": "Иванов Иван",
                        "amount": 15000,
                        "status": "active",
                    }
                ]
            },
        }
    ]

    summary = RiskAnalyzer().analyze(results)

    assert summary.score >= 20
    assert summary.level in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert any(finding.code == "active_debts" for finding in summary.findings)
