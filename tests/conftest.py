import pytest
from django.contrib.auth import get_user_model

from checks.models import Check


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="tester",
        email="tester@example.com",
        password="pass",
    )


@pytest.fixture
def check(db, user):
    return Check.objects.create(
        user=user,
        address="Москва, Тверская, 1",
        cadastral_number="77:01:0004012:1234",
        full_name="Иванов Иван Иванович",
        phone="+79990000000",
        email="owner@example.com",
        inn="770000000000",
    )
