from rest_framework import serializers
from chat_app.models import User, ChatRoom, ChatMessage
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

# 사용자 정보 조회
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("__all__")
        
# 사용자 회원가입
class SignUpSerializer(serializers.ModelSerializer):
    user_name=serializers.CharField(write_only=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id','user_name', 'password','password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2') # password2 필드는 User 모델에 저장하지 않음
        user = User.objects.create_user(
            user_name=validated_data['user_name'],
            password=validated_data['password'],
        )
        return {'user':user}

# 사용자 로그인
class LoginSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('user_name', 'password')

    def validate(self, data):
        user_name = data.get("user_name")
        password = data.get("password")

        try:
            user = User.objects.get(user_name=user_name)
        except User.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials"]})

        if not user.check_password(password):
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials"]})

        return {"user": user}  # user 객체 반환
        
# 채팅방
class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model=ChatRoom
        fields=('id', 'user_id', 'chatroom_title','created_at','topic')
        
# 채팅 메시지
class ChatMessageSerializer(serializers.ModelSerializer):
    chatroom_id = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())
    class Meta:
        model=ChatMessage
        fields=('id','chatroom_id','sender','text','created_at')