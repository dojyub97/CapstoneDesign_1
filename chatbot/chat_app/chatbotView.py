import os
import requests
from django.shortcuts import render, redirect
from dash import html, dcc
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = DjangoDash('dash_app')

app.layout = html.Div([
    dcc.Store(id='session-id', storage_type='session'),  # 세션 저장소
    html.Div(id='message-container', style={'overflow-y': 'auto', 'height': '80%'}),
    dcc.Input(id='chat-input', type='text', placeholder='Type a message...'),
    html.Button('Send', id='send-button', n_clicks=0),
])

API_URL = 'http://127.0.0.1:8000/api/'

def get_auth_headers(request):
    token = request.session.get("access_token")
    if not token:
        return None
    return {'Authorization': f'Bearer {token}'}

# Dash 콜백 함수
@app.callback(
    Output('message-container', 'children'),
    Input('send-button', 'n_clicks'),
    State('chat-input', 'value'),
    State('session-id', 'data'),
    prevent_initial_call=True
)

# 사용자가 입력한 메시지를 채팅방에 전송하는 함수
def send_message(message, chatroomId, headers):
    response = requests.post(
        f'{API_URL}chatroom/{chatroomId}', 
        json={'text': message}, 
        headers=headers
        )
    if response.status_code == 201:
        bot_message = response.json().get('bot_message', {}).get('text', '응답을 받을 수 없습니다.')
        return bot_message
    return 'API 서버와의 통신에 실패했습니다.'

def update_output(n_clicks, value, chatroomId, request):
    if n_clicks is None or not value or chatroomId is None:
        return '메시지를 입력하세요!'

    # 사용자 토큰을 가져와서 API로 메시지 전송
    token = get_auth_headers(request)
    if not token:
        return '로그인이 필요합니다.'
    
    response = send_message(value, chatroomId, token)
    return f'봇의 응답: {response}'

def chatbot_view(request, chatroomId=None):
    # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
    if not request.session.get("access_token"):
        return redirect('chat_app:login')
    
    # access_token을 가져와 템플릿으로 전달
    context = {
        'access_token': request.session.get("access_token"),
        'chatroom_id': chatroomId
    }
    return render(request, 'chat_app/chatbot.html', context)

def main_view(request):
    return render(request, 'chat_app/main.html')

def login_view(request):
    return render(request, 'chat_app/login.html')

def signup_view(request):
    return render(request, 'chat_app/signUp.html')