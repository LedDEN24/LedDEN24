import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from checks.models import Check


@pytest.mark.django_db
def test_authenticated_user_can_create_check(monkeypatch, django_user_model, django_capture_on_commit_callbacks):
    queued = []

    class DelayStub:
        @staticmethod
        def delay(check_id):
            queued.append(check_id)

    monkeypatch.setattr("checks.api.views.process_check", DelayStub)
    user = django_user_model.objects.create_user(username="user", password="pass")
    client = APIClient()
    client.force_authenticate(user=user)

    with django_capture_on_commit_callbacks(execute=True):
        response = client.post(
            reverse("checks-list"),
            {
                "address": "Москва, Тверская 1",
                "cadastral_number": "77:01:0004010:1001",
                "full_name": "Иванов Иван Иванович",
                "phone": "+79990000000",
                "email": "ivanov@example.com",
                "inn": "7700000000",
            },
            format="json",
        )

    assert response.status_code == 201
    check = Check.objects.get()
    assert check.created_by == user
    assert queued == [check.pk]
