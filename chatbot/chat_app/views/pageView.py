from django.shortcuts import render

def main_view(request):
    return render(request, 'chat_app/main.html')

def login_view(request):
    return render(request, 'chat_app/login.html')

def signup_view(request):
    return render(request, 'chat_app/signUp.html')