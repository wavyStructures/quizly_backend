import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from quizly_app.models import Quiz

User = get_user_model()

@pytest.mark.django_db
class TestCreateQuiz:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="anja@example.com",
            username="anja@example.com",
            password="Test123!"
        )

    @pytest.fixture
    def auth_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @patch("quizly_app.utils.generate_quiz_from_youtube")
    def test_create_quiz_success(self, mock_gen, auth_client, user):
        mock_gen.return_value = {
            "title": "My Test Quiz",
            "description": "A test description",
            "questions": [
                {
                    "question_title": "Q1?",
                    "question_options": ["A", "B", "C"],
                    "answer": "A"
                },
                {
                    "question_title": "Q2?",
                    "question_options": ["X", "Y", "Z"],
                    "answer": "Y"
                }
            ]
        }

        url = reverse("create_quiz")
        data = {"url": "https://youtube.com/watch?v=123"}

        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "My Test Quiz"
        assert response.data["description"] == "A test description"
        assert response.data["video_url"] == data["url"]
        assert len(response.data.get("questions", [])) > 0

        quiz = Quiz.objects.get(user=user)

        assert quiz.title == "My Test Quiz"
        assert quiz.questions.count() == 2

        titles = [q.question_title for q in quiz.questions.all()]

        assert "Q1?" in titles
        assert "Q2?" in titles


    def test_create_quiz_requires_auth(self, client):
        url = reverse("create_quiz")
        response = client.post(url, {"url": "x"}, format="json")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]