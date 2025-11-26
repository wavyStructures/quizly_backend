from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from .models import Quiz, Question
from .serializers import (
    QuizSerializer,
    CreateQuizSerializer
)


class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        video_url = serializer.validated_data["url"]

        # Real life: extract metadata from YouTube API
        # Example placeholder
        quiz = Quiz.objects.create(
            user=request.user,
            title="Generated Quiz",
            description="Generated from YouTube URL",
            video_url=video_url
        )

        # Example static question — replace with actual extraction later
        Question.objects.create(
            quiz=quiz,
            question_title="What is shown in the video?",
            question_options=["A", "B", "C", "D"],
            answer="A"
        )

        return Response(
            QuizSerializer(quiz).data,
            status=status.HTTP_201_CREATED
        )


class QuizListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = Quiz.objects.filter(user=request.user)
        return Response(
            QuizSerializer(quizzes, many=True).data,
            status=status.HTTP_200_OK
        )


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User can only access own quizzes
        return Quiz.objects.filter(user=self.request.user)