import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from quizly_app.models import Quiz


@pytest.mark.django_db
class TestCreateQuiz:

    @patch("quizly_app.views.generate_quiz_from_youtube")
    def test_create_quiz_success(self, mock_gen, auth_client, user):
        mock_gen.return_value = {
            "title": "My Test Quiz",
            "description": "A test description",
            "questions": [
                {
                    "question_title": f"Question {i}?",
                    "question_options": [
                        f"Option A{i}",
                        f"Option B{i}",
                        f"Option C{i}",
                        f"Option D{i}",
                    ],
                    "answer": "A",
                }
                for i in range(1, 11)
            ],
        }

        url = reverse("quiz-list")
        data = {"url": "https://youtube.com/watch?v=123"}

        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "My Test Quiz"
        assert response.data["description"] == "A test description"
        assert response.data["video_url"] == data["url"]
        assert len(response.data["questions"]) == 10

        for question in response.data["questions"]:
            assert len(question["question_options"]) == 4

        quiz = Quiz.objects.get(user=user)
        assert quiz.title == "My Test Quiz"
        assert quiz.description == "A test description"
        assert quiz.video_url == data["url"]
        assert quiz.questions.count() == 10


    @patch("quizly_app.views.generate_quiz_from_youtube")
    def test_create_quiz_generator_error(self, mock_gen, auth_client):
        mock_gen.side_effect = ValueError("Could not transcribe audio")

        url = reverse("quiz-list")
        data = {"url": "https://youtube.com/watch?v=123"}

        response = auth_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Could not transcribe audio"

    def test_create_quiz_requires_auth(self, client):
        url = reverse("quiz-list")
        response = client.post(
            url,
            {"url": "https://youtube.com/watch?v=123"},
            format="json",
        )

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]