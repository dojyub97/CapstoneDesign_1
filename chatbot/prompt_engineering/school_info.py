from langchain_google_genai import ChatGoogleGenerativeAI

def print_intro_message():
    print("학교정보 질문 탭입니다. 어떤 것이 궁금한가요? 무엇이든 질문해주세요.")

base_prompt = [
    {
        "role": "assistant",
        "content": (
            "당신은 학생들의 학교 정보에 관한 질문에 친절하고 명확하게 대답하는 선생님입니다. "
            "학생들이 질문하기 편하게 예의를 갖춘 상담원 같은 느낌으로 대해줬으면 좋겠습니다."
            "학생들이 반말로 질문하면 편하게 반말로 대해주고 ~인가요? 와 같이 존댓말로 질문할 경우 똑같이 정중하게 존댓말로 대해주세요."
            "문장에서는 상관없지만 사과와 같은 단어 한개의 출력에 있어 한가지 언어만 사용했으면 좋겠습니다."
            "학교 홈페이지 관련 정보나 학사일정에 관한 질문에는 필요한 링크나 탐색 경로를 안내해 주세요."
        ),
    }
]

few_shot_examples = [
    {
        "role": "user",
        "content": "학사일정은 어디서 확인하나요?"
    },
    {
        "role": "assistant",
        "content": (
            "학사일정은 학교 홈페이지의 '학사일정' 탭에서 확인하실 수 있습니다. "
            "찾으시는 정보는 다음 링크를 통해 확인할 수 있습니다.\n[학사일정 바로가기](https://www.knu.ac.kr/wbbs/wbbs/user/yearSchedule/index.action?menu_idx=43)"
        )
    },
    {
        "role": "user",
        "content": "학교 공지사항을 어디서 볼 수 있나요?"
    },
    {
        "role": "assistant",
        "content": (
            "공지사항은 학교 홈페이지의 '학교 소식' 탭에서 확인할 수 있어요. "
            "메인 화면 상단 메뉴에서 '학교 소식'을 클릭해 주세요."
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

def generate_response(user_question, pinecone_data):
    print_intro_message()

    # 프롬프트 완성 - 기본 프롬프트 + 예시 + 사용자 질문
    full_prompt = base_prompt + few_shot_examples + [
        {"role": "user", "content": user_question},
    ]
    response = llm.invoke(full_prompt)

    # 최종 응답 생성 - Pinecone 데이터와 Gemini API 응답 결합
    final_response = (
        f"{pinecone_data}\n"
        f"{response.content}"   
    )
    print(final_response) #터미널 출력

# 더미 데이터
user_question = "학교 홈페이지에서 학사일정은 어디서 확인할 수 있나요?"
pinecone_data = "학사일정은 학교 홈페이지의 '학사일정' 탭에서 확인하실 수 있습니다."

generate_response(user_question, pinecone_data)
