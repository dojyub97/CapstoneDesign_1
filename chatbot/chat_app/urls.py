from django.urls import path
from .views import *

app_name='chat_app'

urlpatterns = [
    path('', main_view, name='main'),              
    path('login/', login_view, name='login'),      
    path('signup/', signup_view, name='signUp'),   
    path('chatbot/', chatbot_view, name='chatbot') 
]
