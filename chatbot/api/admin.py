from django.contrib import admin
from chat_app.models import User, ChatRoom, ChatMessage

# Register your models here.
admin.site.register(User)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)