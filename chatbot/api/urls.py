from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, getUser, getUserForId

urlpatterns = [
    path('register/', RegisterView.as_view()),
]