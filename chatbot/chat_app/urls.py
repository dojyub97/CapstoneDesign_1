from django.urls import path
from .views import *

app_name = "chat_app"

urlpatterns = [
    path("", login_view, name="login"),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signUp"),
    path("home/", chatbot_view, name="chatbot"),
]
