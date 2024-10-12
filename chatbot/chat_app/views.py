from django.shortcuts import render
import os
import json
import asyncio
import websockets
from dash import html,dcc
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app=DjangoDash('dash_app')

app.layout = html.Div([
    dcc.Input(id='input-message', type='text', placeholder='메시지를 입력하세요...'),
    html.Button('전송', id='submit-button', n_clicks=0),
    html.Div(id='output-container')
])

async def send_message(message):
    async with websockets.connect('ws://127.0.0.1:8000/ws/chat/') as websocket:
        await websocket.send(json.dumps({'message': message}))
        response = await websocket.recv()
        return json.loads(response)['message']

@app.callback(
    Output('output-container', 'children'),
    Input('submit-button', 'n_clicks'),
    Input('input-message', 'value')
)

def update_output(n_clicks, value):
    if n_clicks is None or not value:
        return '메시지를 입력하세요!'

    # 웹소켓을 통해 메시지 전송
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(send_message(value))

    return f'봇의 응답: {response}'

# Create your views here.
def chatbot_view(request):
    return render(request, 'chat_app/index.html')
