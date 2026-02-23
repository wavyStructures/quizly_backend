import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestLogout:

    @pytest.fixture
    def logged_in_client(self, client):
        """Creates a user, logs in, and returns a client with cookies set."""
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


    def test_logout_success(self, logged_in_client):
        url = reverse("logout")

        response = logged_in_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"].startswith("Log-Out successfully")

        assert response.cookies.get("access_token").value == ""
        assert response.cookies.get("refresh_token").value == ""


    def test_logout_without_refresh_token(self, client):
        url = reverse("logout")

        response = client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
