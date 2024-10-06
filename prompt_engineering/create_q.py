from langchain_google_genai import ChatGoogleGenerativeAI

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
    }
]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=300,
    timeout=30,
    max_retries=2
)

def generate_response(user_question, pinecone_data):
    print_intro_message()

    # 프롬프트 완성 - 기본 프롬프트 + 예시 + 사용자 질문
    full_prompt = base_prompt + few_shot_examples + [
        {"role": "user", "content": user_question},
    ]

    response = llm.invoke(full_prompt)
    response_content = response.content

    final_response = (
        f"{pinecone_data}\n"
        f"{response_content}"   
    )
    print(final_response)  # 터미널 출력

# 더미 데이터
user_question = "사과에 대한 문제를 만들어 주세요."
pinecone_data = "과일에 관한 일반 정보가 검색되었습니다."

# 문제 생성
generate_response(user_question, pinecone_data)
