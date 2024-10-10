from rest_framework import serializers
from chat_app.models import User, ChatRoom, ChatMessage
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    id=serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password=serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2=serializers.CharField(
        write_only=True,
        required=True,
    )
    
    class Meta:
        model=User
        fields=('id','username', 'password','password2')
        
    def validate(self, data):
        if data['password']!=data['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return data
    
    def create(self, validated_data):
        user=User.objects.create_user(
            username=validated_data['username'],
            id=validated_data['id']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        token=Token.objects.create(user=user)
        return user

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