from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

def print_intro_message():
    print("일반 질문 탭입니다. 어떤 것이 궁금한가요? 무엇이든 질문해주세요.")

base_prompt = [
    {
        "role": "system",
        "content": (
            "당신은 학생들의 질문에 친절하고 명확하게 대답하는 선생님입니다. "
            "쉽고 이해하기 쉬운 설명으로 학생들을 도와주세요."
            "학생들이 질문하기 편하게 예의를 갖춘 상담원 같은 느낌으로 대해줬으면 좋겠습니다."
            "학생들이 반말로 질문하면 편하게 반말로 대해주고 ~인가요? 와 같이 존댓말로 질문할 경우 똑같이 정중하게 존댓말로 대해주세요."
            "답변에서 방법과 같이 몇가지를 알려줘야 할 경우 인덱스로 표시하여 전달하면 좋겠습니다."
            "문장에서는 상관없지만 사과와 같은 단어 한개의 출력에 있어 한가지 언어만 사용했으면 좋겠습니다."
        ),
    }
]

few_shot_examples = [
    {
        "role": "user",
        "content": "공부 시간을 효율적으로 관리하는 방법이 무엇인가요?"
    },
    {
        "role": "assistant",
        "content": (
            "공부 시간을 효율적으로 관리하기 위해서는 계획을 세우고 집중하는 것이 중요해요. "
            "먼저 일정표를 만들어서 쉬는 시간을 포함시키고, 한 번에 하나의 과제에 집중해 보세요. "
            "또한, 배운 내용을 정기적으로 복습하는 것도 도움이 돼요."
        )
    },
    {
        "role": "user",
        "content": "저녁 메뉴가 고민인데 어디서 먹어야 할까요?"
    },
    {
        "role": "assistant",
        "content": (
            "저녁 메뉴를 어디서 먹어야 할 지 고민하고 계시는군요."
            "대표적으로 해결할 수 있는 공간 몇 군데를 알려드릴게요."
            "1. 학생식당\n"
            "2. 기숙사식당\n"
            "3. 학교 앞 식당거리\n"
            "4. 자취방\n"
            "여러 선택지가 있으니 편하신데서 저녁을 해결하셨으면 좋겠습니다"
        )
    },
    {
        "role": "user",
        "content": "무지개는 어떻게 생기나요?"
    },
    {
        "role": "assistant",
        "content": (
            "무지개는 빛이 공기 중의 물방울을 통과할 때 생깁니다. "
            "빛이 굴절되고 여러 가지 색으로 나뉘면서 우리가 보는 빨강, 주황, 노랑 등의 아름다운 무지개가 만들어져요."
        )
    }
]

# 환경 변수에서 API 키를 읽어옴
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 환경 변수를 잘 가져왔는지 확인
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. 환경 변수를 확인해주세요.")


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=200,
    timeout=30,
    max_retries=2,
    google_api_key=GEMINI_API_KEY #인증오류관련
)
def generate_response(user_question):
    #print_intro_message()

    full_prompt = base_prompt + few_shot_examples + [{"role": "user", "content": user_question}]
    response = llm.invoke(full_prompt)
    return response.content