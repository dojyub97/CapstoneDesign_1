from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from .serializers import *
from urllib.parse import unquote
from chat_app.prompt_engineering import school_info, pdf_info


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
        # 사용자별로 초기 ChatRoom 생성
        initial_topics = ["school-info", "pdf-QnA"]
        for initial_topic in initial_topics:
            ChatRoom.objects.get_or_create(user_id=request.user, topic=initial_topic)

        chatroom = ChatRoom.objects.get(user_id=request.user, topic=topic)

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
class SchoolInfoView(APIView):
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            serializer = ChatMessageSerializer(data=request.data)

            if serializer.is_valid():
                chat_message = serializer.save(chatroom_id=chatroom)
                input_message = serializer.validated_data.get("text")

                # test
                print(input_message)
                # Call prompt-> response bot message
                output_message = school_info.generate_response(input_message)
                # test
                print(output_message)

                bot_message = ChatMessage.objects.create(
                    chatroom_id=chat_message.chatroom_id,
                    sender="system",
                    text=output_message,
                )
                return Response(
                    {
                        "bot_message": ChatMessageSerializer(bot_message).data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND
            )


class pdfQnAView(APIView):
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            chat_serializer = ChatMessageSerializer(data=request.data("chat_data"))
            file_serializer = PDFfileSerializer(data=request.data("file_data"))

            if chat_serializer.is_valid() and file_serializer.is_valid():
                chat = chat_serializer.save(chatroom_id=chatroom)
                file = file_serializer.save()

                input_message = chat_serializer.validated_data.get("text")
                pdf_text = file_serializer.validated_data.get("content")

                # test
                print(input_message)
                # Call prompt-> response bot message

                # pdf 전송
                output_message = pdf_info.generate_response(input_message)
                # test
                print(output_message)

                bot_message = ChatMessage.objects.create(
                    chatroom_id=chat.chatroom_id,
                    sender="system",
                    text=output_message,
                )
                return Response(
                    {
                        "bot_message": ChatMessageSerializer(bot_message).data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(chat_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND
            )
