import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCreateQuiz:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="anja@example.com",
            username="anja",
            password="Test123!"
        )

    @pytest.fixture
    def auth_client(self, client, user):
        client.force_authenticate(user=user)
        return client

    @patch("quizly_app.views.generate_quiz_from_youtube")
    def test_create_quiz_success(self, mock_gen, auth_client, user):
        """
        Creates a quiz by mocking the full YT/Whisper/Gemini pipeline.
        """
        mock_gen.return_value = {
            "title": "My Test Quiz",
        }

        url = reverse("create_quiz")
        data = {"url": "https://youtube.com/watch?v=123"}

        response = auth_client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "My Test Quiz" 
        assert response.data["video_url"] == data["url"]

        assert len(response.data["questions"]) == 1

        assert user.quizzes.count() == 1
        quiz = user.quizzes.first()
        assert user.questions.count() == 1

    def test_create_quiz_requires_auth(self, client):
        url = reverse ("create_quiz")
        response = client.post(url, {"url": "x"}, content_type="application/json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
