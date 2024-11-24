from django.shortcuts import render


def chatbot_view(request):
    return render(request, "chat_app/chatbot.html")


def login_view(request):
    return render(request, "chat_app/login.html")


def signup_view(request):
    return render(request, "chat_app/signUp.html")
