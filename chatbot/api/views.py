from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, generics
from .serializers import RegisterSerializer, UserSerializer,ChatRoomSerializer, ChatMessageSerializer
from chat_app.models import User,ChatRoom,ChatMessage
from chat_app.utils import query_gemini_api
from chat_app.prompt_engineering.general_text import generate_response
# Create your views here.

# User CRUD
class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=RegisterSerializer

# ChatMessage CRUD
@api_view(['GET', 'POST'])
def getChatMessages(request):
    if request.method == 'GET':
        query = ChatMessage.objects.all()
        serializer = ChatMessageSerializer(query, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        chat_message = ChatMessageSerializer(data=request.data)
        if chat_message.is_valid():
            chat_message.save()
            
            # Call Google Gemini API for response
            user_message = chat_message.validated_data.get("text")
            prompt = generate_response(user_message)
            gemini_response = query_gemini_api(prompt)
            
            if gemini_response:
                bot_message = gemini_response.get("response")  # 응답 필드에 맞게 수정
                # 챗봇의 응답 메시지를 추가
                ChatMessage.objects.create(
                    chatroom=chat_message.validated_data['chatroom'],
                    sender='system',
                    text=bot_message
                )
            return Response(chat_message.data, status=status.HTTP_201_CREATED)
        return Response(chat_message.errors, status=status.HTTP_400_BAD_REQUEST)