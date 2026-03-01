from rest_framework import serializers
from .models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    answer = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]

    def get_answer(self, obj):
        """
        Convert 'B' -> full option text, e.g. 'Berlin'
        """
        if not obj.answer:
            return ""

        index = ord(obj.answer.upper()) - ord("A")

        try:
            return obj.question_options[index]
        except (IndexError, TypeError):
            return ""


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]


class CreateQuizSerializer(serializers.Serializer):
    url = serializers.URLField()