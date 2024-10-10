from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import getUser, getUserForId

router=DefaultRouter()
#views에 대한 router 등록
#router.register(r'users',)
urlpatterns = [
    path('chat_app/login'),
    path('chat_app/chat/<int:pk>')
]
