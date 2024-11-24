from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)  # Import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from .serializers import *
from urllib.parse import unquote
from chat_app.prompt_engineering.general_text import generate_response


@permission_classes([AllowAny])
@authentication_classes([])
# 회원가입 apiview
class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


@permission_classes([AllowAny])
@authentication_classes([])
# 로그인 apiview
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get(
                "user"
            )  # This should be added in your serializer's validate method
            access = serializer.validated_data.get("access_token")
            refresh = serializer.validated_data.get("refresh_token")

            return Response(
                {
                    "user_id": user.id,
                    "access_token": access,
                    "refresh_token": refresh,
                },
                status=status.HTTP_200_OK,
            )

        # If serializer is not valid, return error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# 사용자 로그아웃 api view
class LogoutView(APIView):
    def post(self, request):
        try:
            # 세션에서 토큰 삭제
            if "authToken" in request.session:
                del request.session["authToken"]
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# Chatting Room CRUD
class ChatRoomView(APIView):
    def get(self, request, topic):
        # URL 디코딩
        decoded_topic = unquote(topic)

        # 사용자별로 초기 ChatRoom 생성
        initial_topics = ["학교정보", "예상문제"]
        for initial_topic in initial_topics:
            ChatRoom.objects.get_or_create(user_id=request.user, topic=initial_topic)

        chatroom = ChatRoom.objects.get(user_id=request.user, topic=decoded_topic)

        messages = ChatMessage.objects.filter(chatroom_id=chatroom).order_by(
            "created_at"
        )
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(
            {
                "chatroom": ChatRoomSerializer(chatroom).data,
                "chatroom_id": chatroom.id,
                "messages": serializer.data,
            }
        )


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# Chatting message CRUD
class ChatMessageView(APIView):
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            serializer = ChatMessageSerializer(data=request.data)

            if serializer.is_valid():
                chat_message = serializer.save(chatroom_id=chatroom)

                # Call Google Gemini API for response
                user_message = serializer.validated_data.get("text")
                prompt = generate_response(user_message)

                bot_message = ChatMessage.objects.create(
                    chatroom_id=chat_message.chatroom_id, sender="system", text=prompt
                )
                return Response(
                    {
                        "user_message": serializer.data,
                        "bot_message": ChatMessageSerializer(bot_message).data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND
            )
