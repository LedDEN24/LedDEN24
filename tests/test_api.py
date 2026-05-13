import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_check_api_requires_auth(client):
    response = client.get("/api/checks/")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_authenticated_user_can_list_own_checks(client, user, check):
    client.force_login(user)

    response = client.get("/api/checks/")

    assert response.status_code == 200
    assert response.json()["count"] == 1


@pytest.mark.django_db
def test_history_page_renders(client, user, check):
    client.force_login(user)

    response = client.get(reverse("checks:history"))

    assert response.status_code == 200
    assert "Москва" in response.content.decode()
