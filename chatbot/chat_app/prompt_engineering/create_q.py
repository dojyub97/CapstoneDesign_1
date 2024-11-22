"""from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
from chat_app.consumers import retrieve_similar_document

def print_intro_message():
    print("예상문제 관련 질문 탭입니다. 예상문제를 생성해 드릴게요. 질문해 주세요.")

base_prompt = [
    {
        "role": "assistant",
        "content": (
            "당신은 학생들의 예상문제를 친절하고 명확하게 만들어주는 선생님입니다. "
            "학생들이 질문하기 편하게 예의를 갖춘 상담원 같은 느낌으로 대해줬으면 좋겠습니다."
            "학생들이 반말로 질문하면 편하게 반말로 대해주고 ~인가요? 와 같이 존댓말로 질문할 경우 똑같이 정중하게 존댓말로 대해주세요."
            "학생들에게 필요한 예상문제를 제공해 주세요. 객관식 문제는 보기와 정답을 포함하고, "
            "문장에서는 상관없지만 사과와 같은 단어 한개의 출력에 있어 한가지 언어만 사용했으면 좋겠습니다."
            "주관식 문제는 논술형 답변도 가능합니다."
        ),
    }
]

few_shot_examples = [
    {
        "role": "user",
        "content": "수박에 대한 문제를 만들어 주세요."
    },
    {
        "role": "assistant",
        "content": (
            "문제) 1. 수박은 어떤 과일인가요?\n"
            "a. 열대과일입니다.\n"
            "b. 겉이 초록색입니다.\n"
            "c. 속은 빨간색입니다.\n"
            "d. 씨가 존재합니다.\n"
            "e. 넝쿨이 있습니다.\n"
        )
    },
    {
        "role": "user",
        "content": "논술형 문제를 만들어 주세요."
    },
    {
        "role": "assistant",
        "content": (
            "문제) 수박의 주요 특징과 생육 환경에 대해 논하시오.\n"
            "답변: 수박은 열대과일로, 겉이 초록색이고 속은 빨간색이다. 또한, 씨가 있으며 넝쿨에서 자란다. "
            "수박은 따뜻한 기후에서 잘 자라며, 물이 많은 환경을 선호한다."
        )
    },
    {
        "role": "user",
        "content": "객관식 문제를 만들어 주세요."
    },
    {
        "role": "assistant",
        "content": (
            "문제) 다음 중 틀린 것만 고르시오.\n"
            "a. 수박은 지중해 과일이다.\n"
            "b. 수박은 겉이 초록색이고 속이 빨간색이다.\n"
            "c. 수박은 나무에서 자란다.\n"
            "d. 수박은 물이 많은 환경을 선호한다.\n"
            "e. 위 내용 중 틀린 것은 2개이다.\n"
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
    max_tokens=300,
    timeout=30,
    max_retries=2,
    google_api_key=GEMINI_API_KEY #인증오류관련
)

def generate_response(user_question):
    print_intro_message()

    pdf_info_content, _ = retrieve_similar_document(user_question, "QnA")

    # 프롬프트 완성 - 기본 프롬프트 + 예시 + 사용자 질문
    full_prompt = base_prompt + few_shot_examples + [
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": pdf_info_content}
    ]

    response = llm.invoke(full_prompt)
    response_content = response.content

    final_response = (
        f"{pdf_info_content}\n"
        f"{response_content}"   
    )
    print(final_response)  # 터미널 출력
    return final_response"""
