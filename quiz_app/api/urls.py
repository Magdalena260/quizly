from django.urls import path

from .views import QuizDetailView, QuizListView


urlpatterns = [
    path("quizzes/", QuizListView.as_view()),
    path("quizzes/<int:pk>/", QuizDetailView.as_view()),
]