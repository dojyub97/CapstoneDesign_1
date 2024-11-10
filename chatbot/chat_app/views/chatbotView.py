import os
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from dash import html, dcc
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash
from ..models import ChatRoom, ChatMessage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = DjangoDash('dash_app')

app.layout = html.Div([
    dcc.Input(id='input-message', type='text', placeholder='메시지를 입력하세요...'),
    html.Button('전송', id='submit-button', n_clicks=0),
    html.Div(id='output-container'),
    dcc.Store(id='selected-chatroom-id')
])

API_URL = 'http://127.0.0.1:8000/api/'

@login_required
def get_chatrooms(request):
    """채팅방 목록을 반환"""
    chatrooms = ChatRoom.objects.all()
    chatroom_data = [{'id': room.id, 'chatroom_title': room.name} for room in chatrooms]
    return JsonResponse(chatroom_data, safe=False)

@login_required
def chatroom_messages(request, chatroom_id):
    """특정 채팅방의 메시지를 반환"""
    chatroom = ChatRoom.objects.get(id=chatroom_id)
    messages = ChatMessage.objects.filter(chatroom=chatroom).order_by('created_at')
    message_data = [
        {'sender': msg.sender, 'text': msg.text, 'created_at': msg.created_at.isoformat()}
        for msg in messages
    ]
    return JsonResponse(message_data, safe=False)

def send_message(message, chatroom_id, token):
    headers = {'Authorization': f'Token {token}'}
    response = requests.post(f'{API_URL}chat/{chatroom_id}/messages/', json={'text': message}, headers=headers)
    if response.status_code == 200:
        return response.json().get('bot_message', {}).get('text', '응답을 받을 수 없습니다.')
    else:
        return 'API 서버와의 통신에 실패했습니다.'

@app.callback(
    Output('output-container', 'children'),
    Input('submit-button', 'n_clicks'),
    Input('input-message', 'value'),
    State('input-message', 'value'),
    State('selected-chatroom-id', 'data'),
    prevent_initial_call=True
)
def update_output(n_clicks, value, chatroom_id, request):
    if n_clicks is None or not value or chatroom_id is None:
        return '메시지를 입력하세요!'

    # 사용자 토큰을 가져와서 API로 메시지 전송
    token = get_user_token(request)
    if not token:
        return '로그인이 필요합니다.'

    # 비동기 함수 호출에 await 추가
    response = send_message(value, chatroom_id, token)
    return f'봇의 응답: {response}'

def get_user_token(request):
    return request.session.get('authToken')

def chatbot_view(request):
    token=get_user_token(request)
    if not token:
        return redirect('chat_app:login')
    return render(request, 'chat_app/chatbot.html')