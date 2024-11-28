from django.urls import path
from .views import *

app_name = "chat_app"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signUp"),
    path("", chatbot_view, name="home"),
]
