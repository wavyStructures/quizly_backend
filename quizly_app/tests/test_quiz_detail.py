import pytest
from django.urls import reverse
from rest_framework import status
from quizly_app.models import Quiz
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestQuizDetail:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="anja@example.com",
            username="anja",
            password="Test123!"
        )

    @pytest.fixture
    def other_user(self):
        return User.objects.create_user(
            email="x@example.com",
            username="x",
            password="Test123!"
        )

    @pytest.fixture
    def quiz(self, user):
        return Quiz.objects.create(
            user=user,
            title="Original Title",
            description="desc",
            video_url="https://example.com"
        )

    @pytest.fixture
    def auth_client(self, client, user):
        client.force_authenticate(user=user)
        return client


    # ----------------- RETRIEVE -----------------

    def test_get_quiz(self, auth_client, quiz):
        url = reverse("quiz_detail", args=[quiz.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Original Title"

    def test_get_other_users_quiz_denied(self, client, other_user, quiz):
        client.force_authenticate(user=other_user)
        url = reverse("quiz_detail", args=[quiz.id])
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    # ----------------- UPDATE (PATCH) -----------------

    def test_patch_quiz(self, auth_client, quiz):
        url = reverse("quiz_detail", args=[quiz.id])
        response = auth_client.patch(url, {"title": "Updated"}, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated"

    def test_patch_other_users_quiz_denied(self, client, other_user, quiz):
        client.force_authenticate(user=other_user)
        url = reverse("quiz_detail", args=[quiz.id])

        response = client.patch(url, {"title": "SHOULD NOT"}, content_type="application/json")
        assert response.status_code == status.HTTP_404_NOT_FOUND


    # ----------------- DELETE -----------------

    def test_delete_quiz(self, auth_client, quiz):
        url = reverse("quiz_detail", args=[quiz.id])
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Quiz.objects.count() == 0

    def test_delete_other_users_quiz_denied(self, client, other_user, quiz):
        client.force_authenticate(user=other_user)
        url = reverse("quiz_detail", args=[quiz.id])

        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Quiz.objects.count() == 1

