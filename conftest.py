import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        email="anja@example.com",
        username="anja@example.com",
        password="Str0ngPass!123"
    )

@pytest.fixture
def auth_client(api_client, user):
    """
    Logs in via real login endpoint.
    """
    url = reverse("login")

    response = api_client.post(
        url,
        {
            "email": "anja@example.com",
            "password": "Str0ngPass!123"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    api_client.force_authenticate(user=user)

    return api_client
