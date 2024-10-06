from rest_framework import serializers
from chat_app.models import User, ChatRoom, ChatMessage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("__all__")
        # ("id", "user_name", "password")
        
class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model=ChatRoom
        fields=['id', 'user', 'chatroom_title','created_at','topic']
        
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ChatMessage
        fields=['id','chatroom','sender','text','created_at']