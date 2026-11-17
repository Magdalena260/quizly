from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    RegistrationView,
    TokenRefreshView,
)


urlpatterns = [
    path("register/", RegistrationView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
]