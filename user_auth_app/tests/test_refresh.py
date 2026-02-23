import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestTokenRefresh:

    @pytest.fixture
    def logged_in_client(self, client):
        user = User.objects.create_user(
            email="anja@example.com",
            username="anja",
            password="Str0ngPass!123"
        )
        login_url = reverse("login")
        response = client.post(
            login_url,
            {"email": "anja@example.com", "password": "Str0ngPass!123"},
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get("refresh_token")
        
        return APIClient()

    def test_refresh_success(self, logged_in_client):
        url = reverse("token_refresh")
        response = logged_in_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

        assert response.cookies.get("access_token")
        assert response.cookies.get("refresh_token")

    def test_refresh_missing_token(self, client):
        url = reverse("token_refresh")
        response = client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
