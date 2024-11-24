from django.urls import path
from .views import *

app_name = "chat_app"

urlpatterns = [
    path("main/", main_view, name="main"),
    path("", login_view, name="login"),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signUp"),
    path("chatbot/home/", chatbot_view, name="chatbot"),
]
