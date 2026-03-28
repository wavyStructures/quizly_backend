import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="anja@example.com",
        username="anja@example.com",
        password="Str0ngPass!123"
    )


@pytest.fixture
def other_user():
    return User.objects.create_user(
        email="other@example.com",
        username="other@example.com",
        password="Str0ngPass!123"
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    response = client.post("/api/login/", {
        "username": user.username,
        "password": "Str0ngPass!123"
    }, format="json")

    assert response.status_code == 200
    return client


@pytest.fixture
def other_auth_client(other_user):
    client = APIClient()
    response = client.post("/api/login/", {
        "username": other_user.username,
        "password": "Str0ngPass!123"
    }, format="json")

    assert response.status_code == 200
    return client