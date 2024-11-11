from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from .serializers import *

from rest_framework.authtoken.models import Token

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication  # Import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from chat_app.utils import query_gemini_api
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
            user = serializer.validated_data.get('user')  # This should be added in your serializer's validate method
            access = serializer.validated_data.get('access_token')
            refresh= serializer.validated_data.get('refresh_token')
            
            request.session['access_token']=access
            # 여러 개의 채팅방일 경우 all로 변경하기
            chatroom=ChatRoom.objects.filter(user_id=user).first()
            if not chatroom:
                chatroom=ChatRoom.objects.create(
                    user_id=user,
                    chatroom_title="New Chat!",
                    topic="학교정보"  # Replace "default_topic" with an actual default topic
                )
            
            return Response({
                'user_id': user.id,
                'access_token': access,
                'refresh_token': refresh,
                'chatroom_id': chatroom.id
            }, status=status.HTTP_200_OK)

        # If serializer is not valid, return error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication]) 
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
@authentication_classes([JWTAuthentication]) 
# Chatting Room CRUD
class ChatRoomView(APIView):
    def get(self, request):
        chatrooms = ChatRoom.objects.filter(user_id=request.user)
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        user=request.user
        chatrooms = ChatRoom.objects.filter(user_id=user)
        serializer = ChatRoomSerializer(chatrooms, many=True)
        if not ChatRoom.objects.filter(user_id=user, topic__isnull=False).exists():
            chatroom=ChatRoom.objects.create(
                    user_id=user,
                    chatroom_title="New Chat!",
                    topic="학교정보"  # Replace "default_topic" with an actual default topic
                )
            serializer = ChatRoomSerializer(chatroom)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            chatrooms = ChatRoom.objects.filter(user_id=user)
            serializer = ChatRoomSerializer(chatrooms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication]) 
# Chatting message CRUD
class ChatMessageView(APIView):
    def get(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            messages = ChatMessage.objects.filter(chatroom_id=chatroom).order_by('created_at')
            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            return Response({'error':'chatroom_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request,chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            serializer = ChatMessageSerializer(data=request.data)
            
            if serializer.is_valid():
                chat_message=serializer.save(chatroom_id=chatroom)
            
                # Call Google Gemini API for response
                user_message = serializer.validated_data.get("text")
                prompt = generate_response(user_message)
                
                bot_message=ChatMessage.objects.create(
                    chatroom_id=chat_message.chatroom_id,
                    sender='system',
                    text=prompt
                )
                return Response({
                    'user_message':serializer.data,
                    'bot_message':ChatMessageSerializer(bot_message).data
                }, status=status.HTTP_201_CREATED)
                
                return Response({'error': 'Gemini API 응답 실패'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # gemini_response = query_gemini_api(prompt)
                # if gemini_response:
                #     bot_message=ChatMessage.objects.create(
                #         chatroom_id=chat_message.chatroom_id,
                #         sender='system',
                #         text=gemini_response
                #     )
                #     return Response({
                #         'user_message':serializer.data,
                #         'bot_message':ChatMessageSerializer(bot_message).data
                #         }, status=status.HTTP_201_CREATED)
                
                # return Response({'error': 'Gemini API 응답 실패'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)