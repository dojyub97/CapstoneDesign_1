import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .prompt_engineering import general_text
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        #response = await chain.ainvoke({"input" : message })
        response = general_text.generate_response(message)
        await self.send(text_data=json.dumps({"message": response + "\n"}))
