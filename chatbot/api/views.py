from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import UserSerializer,ChatRoomSerializer, ChatMessageSerializer
from chat_app.models import User,ChatRoom,ChatMessage
from chat_app.utils import query_gemini_api
# Create your views here.

# User CRUD
@api_view(['GET','POST'])
def getUser(request):
    if request.method == 'GET':
        query = User.objects.all()
        serializer = UserSerializer(query,many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        user = UserSerializer(data=request.data)
        if user.is_valid():
            user.save()
            return Response(user.data)
        return Response(user.errors,status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def getUserForId(request,id):
    try:
        query = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'error' : {
        'code' : 404,
        'message' : "Article not found!"
    }}, status = status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(query)
        return Response(serializer.data)
    elif request.method=='PUT':
        user = UserSerializer(query,data=request.data)
        if user.is_valid():
            user.save()
            return Response(user.data)
        return Response(user.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method=='DELETE':
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# ChatRoom CRUD
@api_view(['GET', 'POST'])
def getChatRooms(request):
    if request.method=='GET':
        query=ChatRoom.objects.all()
        serializer=ChatRoomSerializer(query, many=True)
        return Response(serializer.data)
    elif request.method=='POST':
        chatroom=ChatRoomSerializer(data=request.data)
        if chatroom.is_valid():
            chatroom.save()
            return Response(chatroom.data, status=status.HTTP_201_CREATED)
        return Response(chatroom.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def getChatRoomForId(request, id):
    try:
        query=ChatRoom.objects.get(id=id)
    except ChatRoom.DoesNotExist:
        return Response({'error': {
            'code': 404,
            'message': "ChatRoom not found!"
            }}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method=='GET':
        serializer=ChatRoomSerializer(query)
        return Response(serializer.data)
    elif request.method=='PUT':
        chatroom=ChatRoomSerializer(query, data=request.data)
        if chatroom.is_valid():
            chatroom.save()
            return Response(chatroom.data)
        return Response(chatroom.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method=='DELETE':
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            gemini_response = query_gemini_api(user_message)
            
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

@api_view(['GET', 'PUT', 'DELETE'])
def getChatMessageForId(request, id):
    try:
        query = ChatMessage.objects.get(id=id)
    except ChatMessage.DoesNotExist:
        return Response({'error': {
            'code': 404,
            'message': "ChatMessage not found!"
        }}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ChatMessageSerializer(query)
        return Response(serializer.data)
    elif request.method == 'PUT':
        chat_message = ChatMessageSerializer(query, data=request.data)
        if chat_message.is_valid():
            chat_message.save()
            return Response(chat_message.data)
        return Response(chat_message.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)