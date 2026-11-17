from django.contrib import admin

from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """Edit questions directly inside a quiz."""

    model = Question
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Manage quizzes in the admin panel."""

    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "owner__username")
    list_filter = ("created_at",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Manage individual quiz questions."""

    list_display = ("question_title", "quiz", "answer")
    search_fields = ("question_title",)