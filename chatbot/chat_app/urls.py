from django.urls import path
from .views import chatbot_view

urlpatterns = [
    path('chat/', chatbot_view,name='chat_view'),   # Dash 앱을 위한 Django view
]
