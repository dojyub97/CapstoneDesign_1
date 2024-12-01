from django.shortcuts import render, redirect


def chatbot_view(request):
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "access_token" in request.session:
        # 세션에서 Access Token 가져오기
        token = request.session.get("access_token")

    # 2. Access Token 검증
    if not token:
        return redirect("chat_app:login")

    return render(request, "chat_app/chatbot.html")


def login_view(request):
    return render(request, "chat_app/login.html")


def signup_view(request):
    return render(request, "chat_app/signUp.html")
