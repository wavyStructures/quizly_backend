import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestLogin:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="anja@example.com",
            username="anja",
            password="Str0ngPass!123"
        )

    def test_login_success(self, client, user):
        url = reverse("login")
        data = {"email": "anja@example.com", "password": "Str0ngPass!123"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data
        assert response.cookies.get("access_token")
        assert response.cookies.get("refresh_token")

    def test_login_wrong_credentials(self, client, user):
        url = reverse("login")
        data = {"email": "anja@example.com", "password": "Str0ngPass!123"}
        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
