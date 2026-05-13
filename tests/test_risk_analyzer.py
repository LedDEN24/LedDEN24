import pytest

from checks.models import Check, ParserResult
from checks.services.risk_analyzer import RiskAnalyzer


@pytest.mark.django_db
def test_risk_analyzer_detects_bankruptcy_and_identity_match(django_user_model):
    user = django_user_model.objects.create_user(username="user", password="pass")
    check = Check.objects.create(
        created_by=user,
        address="Москва, Тверская 1",
        full_name="Иванов Иван Иванович",
        inn="7700000000",
    )
    parser_result = ParserResult.objects.create(
        verification=check,
        source="efrsb",
        status="success",
        payload={"items": [{"text": "Иванов Иван Иванович банкрот наблюдение 7700000000"}]},
        matched_fields=["full_name", "inn"],
    )

    score, risks = RiskAnalyzer().analyze(check, [parser_result])

    assert score >= 35
    assert {risk["code"] for risk in risks} >= {"bankruptcy", "identity_match_in_risk_source"}
