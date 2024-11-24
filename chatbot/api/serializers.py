from rest_framework import serializers
from chat_app.models import User, ChatRoom, ChatMessage
from rest_framework_simplejwt.tokens import RefreshToken
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
        user = User(
            user_name=validated_data['user_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
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

        if User.objects.filter(user_name=user_name).first():
            user = User.objects.get(user_name=user_name)
            if not user.check_password(password):
                raise serializers.ValidationError('잘못된 비밀번호입니다.')
            else:
                token=RefreshToken.for_user(user)
                refresh=str(token)
                access=str(token.access_token)
                data={
                    'user': user,
                    'refresh_token': refresh,
                    'access_token' : access,
                }
                return data
        else:
            raise serializers.ValidationError('존재하지 않는 사용자입니다.')
        
    
# 채팅방
class ChatRoomSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model=ChatRoom
        fields=('user_id', 'chatroom_title','created_at','topic')
        
# 채팅 메시지
class ChatMessageSerializer(serializers.ModelSerializer):
    chatroom_id = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())
    class Meta:
        model=ChatMessage
        fields=('chatroom_id','sender','text','created_at')