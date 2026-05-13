from __future__ import annotations

import unittest

from analysis.risk_engine import RiskEngine, Severity


class RiskEngineTests(unittest.TestCase):
    def test_bankruptcy_and_debts_raise_critical_score(self) -> None:
        aggregated = {
            "debts": [{"amount": 700000, "debtor_name": "Иванов И.И."}],
            "court_cases": [],
            "bankruptcy_records": [{"case_number": "A40-1/2024", "debtor_name": "Иванов И.И."}],
            "encumbrances": [],
            "ownership_transitions": [],
            "ads": [],
            "fraud_matches": [],
            "matches": [],
        }

        score, findings = RiskEngine().evaluate(aggregated)

        self.assertGreaterEqual(score, 50)
        self.assertTrue(any(finding.severity == Severity.CRITICAL for finding in findings))
        self.assertIn("bankruptcy_found", {finding.code for finding in findings})

    def test_suspicious_ads_have_bounded_score_impact(self) -> None:
        aggregated = {
            "debts": [],
            "court_cases": [],
            "bankruptcy_records": [],
            "encumbrances": [],
            "ownership_transitions": [],
            "ads": [{"is_suspicious": True} for _ in range(10)],
            "fraud_matches": [],
            "matches": [],
        }

        score, findings = RiskEngine().evaluate(aggregated)

        self.assertEqual(score, 18)
        self.assertEqual(findings[0].code, "suspicious_ads")


if __name__ == "__main__":
    unittest.main()
