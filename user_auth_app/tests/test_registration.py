import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestRegistration:

    def test_register_success(self, client):
        url = reverse("register")
        data = {
            "username": "anja",
            "email": "anja@example.com",
            "password": "Str0ngPass!123",
            "confirmed_password": "Str0ngPass!123"
        }

        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["detail"] == "User created successfully!"
        assert User.objects.filter(email="anja@example.com").exists()


    def test_register_password_mismatch(self, client):
        url = reverse("register")
        data = {
            "username": "anja",
            "email": "anja@example.com",
            "password": "abc123",
            "confirmed_password": "other123"
        }

        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data


    def test_register_missing_email(self, client):
        url = reverse("register")
        data = {
            "username": "anja",
            "password": "Str0ngPass123",
            "confirmed_password": "Str0ngPass123"
        }

        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST




