from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from .serializers import *
from urllib.parse import unquote
from chat_app.prompt_engineering import school_info, pdf_info


#내가 넣은거 
from django.http import JsonResponse
from chat_app.models import ChatRoom

@permission_classes([AllowAny])
@authentication_classes([])
# 회원가입 apiview
class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


@permission_classes([AllowAny])
@authentication_classes([])
# 로그인 apiview
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get(
                "user"
            )  # This should be added in your serializer's validate method
            access = serializer.validated_data.get("access_token")
            refresh = serializer.validated_data.get("refresh_token")

            request.session["refresh_token"] = refresh
            request.session["access_token"] = access
            return Response(
                {
                    "user_id": user.id,
                    "access_token": access,
                    "refresh_token": refresh,
                },
                status=status.HTTP_200_OK,
            )

        # If serializer is not valid, return error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# 사용자 로그아웃 api view
class LogoutView(APIView):
    def post(self, request):
        try:
            # 세션에서 토큰 삭제
            if "access_token" in request.session:
                del request.session["access_token"]
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# Chatting Room CRUD
class ChatRoomView(APIView):
    def get(self, request, topic):
        print("chatroomView안에는 들어옴")

        initial_topics = ["school-info", "pdf-QnA"]
        for initial_topic in initial_topics:
            ChatRoom.objects.get_or_create(user_id=request.user, topic=initial_topic)

        chatroom = ChatRoom.objects.get(user_id=request.user, topic=topic)

        if not chatroom:
            # 사용자별로 초기 ChatRoom 생성
            initial_topics = ["school-info", "pdf-QnA"]
            for initial_topic in initial_topics:
                ChatRoom.objects.get_or_create(
                    user_id=request.user, topic=initial_topic
                )

        messages = ChatMessage.objects.filter(chatroom_id=chatroom).order_by(
            "created_at"
        )
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(
            {
                "chatroom": ChatRoomSerializer(chatroom).data,
                "chatroom_id": chatroom.id,
                "messages": serializer.data,
            }
        )


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# 학사 정보 api
class SchoolInfoView(APIView):
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            serializer = ChatMessageSerializer(data=request.data)

            if serializer.is_valid():
                chat_message = serializer.save(chatroom_id=chatroom)
                input_message = serializer.validated_data.get("text")

                # Call prompt-> response bot message
                output_message = school_info.generate_response(input_message)

                bot_message = ChatMessage.objects.create(
                    chatroom_id=chat_message.chatroom_id,
                    sender="system",
                    text=output_message,
                )

                bot_serializer = ChatMessageSerializer(data=bot_message.data)
                bot_serializer.save(chatroom_id=chatroom)

                return Response(
                    {
                        "sender": bot_message.sender,
                        "text": bot_message.text,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND
            )


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# Chatting message CRUD
class pdfQnAView(APIView):
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            chat_serializer = ChatMessageSerializer(data=request.data("chat_data"))
            file_serializer = PDFfileSerializer(data=request.data("file_data"))

            if chat_serializer.is_valid() and file_serializer.is_valid():
                chat = chat_serializer.save(chatroom_id=chatroom)
                file_serializer.save()

                input_message = chat_serializer.validated_data.get("text")
                pdf_text = file_serializer.validated_data.get("content")

                # test
                print(input_message)
                print(pdf_text)
                # Call prompt-> response bot message

                # pdf_info: generate_response(user_question, class_material)
                output_message = pdf_info.generate_response(input_message, pdf_text)
                # test
                print(output_message)

                bot_message = ChatMessage.objects.create(
                    chatroom_id=chat.chatroom_id,
                    sender="system",
                    text=output_message,
                )
                return Response(
                    {
                        "bot_message": ChatMessageSerializer(bot_message).data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(chat_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND
            )


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chat_app.prompt_engineering.차세대카테고리찾기 import chatbot_rag
import json
#from chat_app.테스트 import 테스트

# 실행할 함수 정의
def 카테고리검색기(input_string):
    # 받은 문자열을 처리하고 결과 반환 (예: 역순 처리)
    print("process_string 에서 받은 입력값 : ",input_string)
#    print(테스트())
    챗봇실행결과=chatbot_rag(input_string)
    print(챗봇실행결과)
    #테스트용 : return input_string[::-1]
    return 챗봇실행결과

@csrf_exempt  # CSRF 검증을 끄는 데코레이터 (테스트용)
def 차세대카테고리검색(request):
    if request.method == "POST":
        print("def차세대카테고리검색까지 들어오나?")
        print("request 에 뭐가 들어있을까?: ",request)
        try:
            # 클라이언트로부터 받은 데이터 처리
            data = json.loads(request.body)
            input_string = data.get("string", "")
            
            # 받은 문자열로 함수를 실행
            result = 카테고리검색기(input_string)
            print("카테고리검색기 실행 직후")
            # 결과를 클라이언트로 반환
            return JsonResponse({"result": result}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)