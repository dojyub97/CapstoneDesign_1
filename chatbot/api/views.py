from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from django.http import JsonResponse

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

            user.refresh_token = refresh
            user.save()

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


class TokenRefreshView(APIView):
    def post(self, request):
        access_token = request.header.get("Authorization").split(" ")[1]
        refresh_token = request.data.get("refresh_token")

        if not access_token:
            return Response(
                {"error": "Access token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filer(refresh_token=refresh_token).first()
        if user:
            try:
                # Refresh Token으로 새로운 Access Token 생성
                token = RefreshToken(refresh_token)
                new_access = str(token.access_token)

                return Response({"access_token": new_access}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(
            {"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED
        )

    def get(self, request):
        return Response({"message": "Token is valid."}, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# 사용자 로그아웃 api view
class LogoutView(APIView):
    def post(self, request):
        try:
            # 세션에서 토큰 삭제
            if "access_token" in request.session:
                del request.session["access_token"]
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# Chatting Room CRUD
class ChatRoomView(APIView):
    def get(self, request, topic):

        initial_topics = ["school-info", "pdf-QnA"]
        for initial_topic in initial_topics:
            ChatRoom.objects.get_or_create(user_id=request.user, topic=initial_topic)

        chatroom = ChatRoom.objects.get(user_id=request.user, topic=topic)

        if not chatroom:
            # 사용자별로 초기 ChatRoom 생성
            initial_topics = ["school-info", "pdf-QnA"]
            for initial_topic in initial_topics:
                ChatRoom.objects.get_or_create(
                    user_id=request.user, topic=initial_topic
                )

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
# 학사 정보 api
class SchoolInfoView(APIView):
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            serializer = ChatMessageSerializer(data=request.data)

            if serializer.is_valid():
                chat_message = serializer.save(chatroom_id=chatroom)
                input_message = serializer.validated_data.get("text")

                # Call prompt-> response bot message
                output_message = school_info.generate_response(input_message)

                bot_message = ChatMessage.objects.create(
                    chatroom_id=chat_message.chatroom_id,
                    sender="system",
                    text=output_message,
                )

                bot_serializer = ChatMessageSerializer(bot_message)

                return Response(bot_serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND
            )


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# pdf+예상질문 api
class pdfQnAView(APIView):
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            chat_data = request.data.get("chat_data")
            file_data = request.data.get("file_data")

            chat_serializer = ChatMessageSerializer(data=chat_data)
            file_serializer = PDFfileSerializer(data=file_data)

            if chat_serializer.is_valid() and file_serializer.is_valid():
                chat = chat_serializer.save(chatroom_id=chatroom)
                file_serializer.save()

                input_message = chat_serializer.validated_data.get("text")
                pdf_text = file_serializer.validated_data.get("content")
                
                print(pdf_text)

                # pdf_info: generate_response(user_question, class_material)
                output_message = pdf_info.generate_response(input_message, pdf_text)

                bot_message = ChatMessage.objects.create(
                    chatroom_id=chat.chatroom_id,
                    sender="system",
                    text=output_message,
                )

                bot_serializer = ChatMessageSerializer(bot_message)

                return Response(bot_serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            # Return validation errors
            errors = {
                "chat_errors": chat_serializer.errors,
                "file_errors": file_serializer.errors,
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND
            )
