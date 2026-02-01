from django.contrib import admin
from .models import Quiz  

@admin.register(Quiz)
class QuizletAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at") 
    list_filter = ("user",)
    search_fields = ("title", "user__email")