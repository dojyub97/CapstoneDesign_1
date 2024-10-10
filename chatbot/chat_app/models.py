from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
    password=models.CharField(max_length=128)
    user_name=models.CharField(max_length=100)
    
    def __str__(self):
        return self.user_name
    
class ChatRoom(models.Model):
    TOPIC_CHOICES=[
        ('school_info', '학교정보'),
        ('pdf_questions','교재관련질문'),
        ('QnA','예상문제')
    ]
    
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms')
    chatroom_title=models.CharField(max_length=100, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    topic=models.CharField(max_length=20, choices=TOPIC_CHOICES)
    
class ChatMessage(models.Model):
    chatroom=models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', null=True)
    
    sender_choices=[
        ('user','사용자'),
        ('system','시스템'),
    ]
    sender=models.CharField(max_length=10, choices=sender_choices)
    gemini_output=models.TextField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return self.sender