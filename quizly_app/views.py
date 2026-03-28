from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Quiz, Question
from .serializers import QuizSerializer, CreateQuizSerializer
from .utils import generate_quiz_from_youtube


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        print("REQUEST.DATA:", request.data)


        serializer = CreateQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        video_url = serializer.validated_data["url"]

        try:
            data = generate_quiz_from_youtube(video_url)
        except ValueError as e:
            print("CREATE QUIZ ERROR:", repr(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        quiz = Quiz.objects.create(
            user=request.user,
            title=data["title"],
            description=data["description"],
            video_url=video_url
        )

        for q in data["questions"]:
            Question.objects.create(
                quiz=quiz,
                question_title=q["question_title"],
                question_options=q["question_options"],
                answer=q["answer"]
            )

        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
    
   