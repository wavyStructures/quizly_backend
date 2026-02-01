from django.db import models
from django.conf import settings

class Quiz(models.Model):
    """
    Represents a quiz object in the system.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Represents a question object in the system.
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    ) 
    question_title = models.CharField(max_length=255)
    question_options = models.JSONField()  # list of strings
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

