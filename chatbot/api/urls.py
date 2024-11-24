from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("chatroom/", ChatRoomView.as_view(), name="chatroom"),
    path("chatroom/<str:topic>/", ChatRoomView.as_view(), name="chat-room"),
    path(
        "chatroom/<int:chatroom_id>/message/",
        ChatMessageView.as_view(),
        name="chat-message",
    ),
]
