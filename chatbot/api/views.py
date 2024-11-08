from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import *

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from chat_app.utils import query_gemini_api
from chat_app.prompt_engineering.general_text import generate_response

@permission_classes([AllowAny])
@authentication_classes([])
# 회원가입 apiview
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
@authentication_classes([])
# 로그인 apiview
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            type(user)
            token, created = Token.objects.get_or_create(user=user)
            request.session['authToken'] = token.key
            return Response({'authToken': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
# 사용자 로그아웃 api view
class LogoutView(APIView):
    def post(self, request):
        try:
            # 세션에서 토큰 삭제
            if 'authToken' in request.session:
                del request.session['authToken']
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
# Chatting Room CRUD
class ChatRoomView(APIView):
    def get(self, request):
        user=request.user
        chat_room=ChatRoom.objects.filter(user=user)
        serializer=ChatRoomSerializer(chat_room, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
# Chatting message CRUD
class ChatMessageView(APIView):
    def get(self, request):
        chatroom_id=request.query_params.get('chatroom_id')
        if chatroom_id:
            query=ChatMessage.objects.filter(chat_room_id=chatroom_id)
            serializer = ChatMessageSerializer(query, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error':'chatroom_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        chat_message = ChatMessageSerializer(data=request.data)
        if chat_message.is_valid():
            chat_message.save()
            
            # Call Google Gemini API for response
            user_message = chat_message.validated_data.get("text")
            prompt = generate_response(user_message)
            gemini_response = query_gemini_api(prompt)
            
            if gemini_response:
                bot_message_text = gemini_response.get("response")  # 응답 필드에 맞게 수정
                bot_message=ChatMessage.objects.create(
                    chatroom=chat_message.validated_data.get('chatroom_id'),
                    sender='system',
                    text=bot_message_text
                )
                return Response({
                    'user_message':chat_message.data,
                    'bot_message':ChatMessageSerializer(bot_message).data
                    }, status=status.HTTP_201_CREATED)
            
            return Response({'error': 'Gemini API 응답 실패'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(chat_message.errors, status=status.HTTP_400_BAD_REQUEST)