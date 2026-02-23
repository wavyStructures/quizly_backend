import pytest
from django.urls import reverse
from rest_framework import status
from quizly_app.models import Quiz
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestQuizList:
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="a@example.com",
            username="a",
            password="Test123!"
        )

    @pytest.fixture
    def other_user(self):
        return User.objects.create_user(
            email="b@example.com",
            username="b",
            password="Test123!"
        )

    @pytest.fixture
    def auth_client(self, client, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return APIClient()

    @pytest.fixture
    def sample_quizzes(self, user, other_user):
        Quiz.objects.create(user=user, title="Q1", video_url="a")
        Quiz.objects.create(user=user, title="Q2", video_url="b")
        Quiz.objects.create(user=other_user, title="Foreign Q", video_url="x")

    def test_list_only_own_quizzes(self, auth_client, sample_quizzes):
        url = reverse("quiz_list")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        titles = [q["title"] for q in response.data]

        assert "Q1" in titles
        assert "Q2" in titles
        assert "Foreign Q" not in titles

    def test_list_requires_auth(self, client):
        url = reverse("quiz_list")
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED