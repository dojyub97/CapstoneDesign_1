import json
from channels.generic.websocket import WebsocketConsumer

###########################gemini api를 쓰기 위한 위한 설정
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
GEMINI_API_KEY = "AIzaSyD1XqpujsnPRgTBdH3encXK4zWxlELKlRo"
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY)
output_parser = StrOutputParser()
prompt = ChatPromptTemplate.from_messages(
    [ ("system","일반적인 답변을 해주세요"), 
     ("user","{input}") ]
)
chain = prompt | llm | output_parser
##############################gemini api를 쓰기 위한 위한 설정


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        response = chain.invoke({"input" : message })

        self.send(text_data=json.dumps({"message": response + "\n"}))
