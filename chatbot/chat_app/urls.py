from django.urls import path
from .chatbotView import *

app_name='chat_app'

urlpatterns = [
    # path('', main_view, name='main'), 
    path('', login_view, name='login'),             
    path('login/', login_view, name='login'),      
    path('signup/', signup_view, name='signUp'),   
    path('chatbot/<int:chatroomId>', chatbot_view, name='chatbot'),
]
