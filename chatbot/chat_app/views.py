from django.shortcuts import render, redirect
import os
import json
import requests
from dash import html, dcc
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
from .models import ChatRoom, ChatMessage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = DjangoDash('dash_app')

app.layout = html.Div([
    dcc.Input(id='input-message', type='text', placeholder='메시지를 입력하세요...'),
    html.Button('전송', id='submit-button', n_clicks=0),
    html.Div(id='output-container')
])

API_URL = 'http://127.0.0.1:8000/api/'

def chatroom_detail(request, chatroom_id):
    chatroom = ChatRoom.objects.get(id=chatroom_id)
    messages = ChatMessage.objects.filter(chatroom=chatroom).order_by('created_at')
    # 상세 정보 관련 로직 추가 가능

def send_message(message, token):
    headers = {'Authorization': f'Token {token}'}
    response = requests.post(f'{API_URL}chat/', json={'message': message}, headers=headers)
    if response.status_code == 200:
        return response.json().get('message', '응답을 받을 수 없습니다.')
    else:
        return 'API 서버와의 통신에 실패했습니다.'

@app.callback(
    Output('output-container', 'children'),
    Input('submit-button', 'n_clicks'),
    Input('input-message', 'value')
)
def update_output(n_clicks, value,request):
    if n_clicks is None or not value:
        return '메시지를 입력하세요!'

    # 사용자 토큰을 가져와서 API로 메시지 전송
    token = get_user_token(request)
    if not token:
        return '로그인이 필요합니다.'

    # 비동기 함수 호출에 await 추가
    response = send_message(value, token)
    return f'봇의 응답: {response}'

def get_user_token(request):
    return request.session.get('authToken')

def main_view(request):
    return render(request, 'chat_app/main.html')

def login_view(request):
    return render(request, 'chat_app/login.html')

def signup_view(request):
    return render(request, 'chat_app/signUp.html')

def chatbot_view(request):
    token=get_user_token(request)
    if not token:
        return redirect('chat_app:login')
    return render(request, 'chat_app/chatbot.html')