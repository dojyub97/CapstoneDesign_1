from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, user_name, password=None):
        if not user_name:
            raise ValueError("The user must have a username")

        user = self.model(user_name=user_name)
        user.set_password(password)
        user.save(using=self._db)

        # 저장된 user 객체의 ID 확인
        if not user.id:
            raise ValueError("User ID was not assigned properly.")

        return user

    def create_superuser(self, user_name, password=None):
        user = self.create_user(user_name=user_name, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)  # 활성화 필드
    is_staff = models.BooleanField(default=False)  # 관리자 권한 필드
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "user_name"

    def __str__(self):
        return self.user_name


class ChatRoom(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatroom")
    chatroom_title = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    topic_choices = [
        ("학교정보", "school_life"),
        ("예상문제", "pdf_questions"),
    ]
    topic = models.CharField(max_length=50, choices=topic_choices, null=False)


class ChatMessage(models.Model):
    chatroom_id = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender_choices = [
        ("user", "사용자"),
        ("system", "시스템"),
    ]
    sender = models.CharField(max_length=10, choices=sender_choices)
    text = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender


class File(models.Model):
    file_name = models.CharField(max_length=255)
    content = models.BinaryField()
