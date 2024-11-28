from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("chatroom/<str:topic>/", ChatRoomView.as_view(), name="chat-room"),
    path(
        "chatmessage/school-info/<int:chatroom_id>/",
        SchoolInfoView.as_view(),
        name="school-info",
    ),
    path(
        "chatmessage/pdf-QnA/<int:chatroom_id>/",
        pdfQnAView.as_view(),
        name="pdf-QnA",
    ),
]
