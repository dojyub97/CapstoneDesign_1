from langchain_google_genai import ChatGoogleGenerativeAI

def print_intro_message():
    print("PDF 관련 질문 탭입니다. 무엇을 도와드릴까요? 질문해 주세요.")

base_prompt = [
    {
        "role": "assistant",
        "content": (
            "당신은 학생들의 PDF 관련 질문에 친절하고 명확하게 답변하는 선생님입니다. "
            "학생들이 질문하기 편하게 예의를 갖춘 상담원 같은 느낌으로 대해줬으면 좋겠습니다."
            "학생들이 반말로 질문하면 편하게 반말로 대해주고 ~인가요? 와 같이 존댓말로 질문할 경우 똑같이 정중하게 존댓말로 대해주세요."
            "문장에서는 상관없지만 사과와 같은 단어 한개의 출력에 있어 한가지 언어만 사용했으면 좋겠습니다."
            "PDF 파일과 관련된 질문에 대해 요약 요청이나 파일 상태에 대한 안내를 제공해 주세요."
        ),
    }
]

few_shot_examples = [
    {
        "role": "user",
        "content": "파일을 요약해 줄 수 있나요?"
    },
    {
        "role": "assistant",
        "content": (
            "먼저 PDF 파일을 업로드해 주세요. 업로드된 파일이 없으면 요약을 진행할 수 없습니다."
        )
    },
    {
        "role": "user",
        "content": "파일 요약을 해주세요."
    },
    {
        "role": "assistant",
        "content": (
            "파일 요약을 요청하셨네요. 최소 5줄, 최대 100줄로 요약해드리겠습니다. "
            "PDF 파일이 이미 업로드된 상태인지 확인해주세요."
        )
    }
]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=200,
    timeout=30,
    max_retries=2
)

def generate_response(user_question, pinecone_data, file_content=None, min_lines=5, max_lines=100):
    print_intro_message()

    # 프롬프트 완성 - 기본 프롬프트 + 예시 + 사용자 질문
    full_prompt = base_prompt + few_shot_examples + [
        {"role": "user", "content": user_question},
    ]

    if file_content is None:
        response_content = "파일이 업로드되지 않았습니다. PDF 파일을 먼저 업로드해 주세요."
    else:
        full_prompt.append({
            "role": "assistant",
            "content": (
                f"요약을 요청하셨네요. 요약을 최소 {min_lines}줄, 최대 {max_lines}줄로 제한하여 제공하겠습니다."
            )
        })
        full_prompt.append({
            "role": "user",
            "content": file_content  # 파일 내용을 추가
        })

        response = llm.invoke(full_prompt)
        response_content = response.content

    final_response = (
        f"{pinecone_data}\n"
        f"{response_content}"
    )
    print(final_response)  # 터미널 출력

# 더미 데이터
user_question = "파일 요약을 해주세요."
pinecone_data = "PDF 파일의 내용이 여기 있습니다."

# 업로드된 파일 내용(더미데이터)
file_content = (
    "스네이크버드는 뱀과 새의 모습을 닮은 귀여운 생물체입니다. "
    "스네이크버드의 주요 먹이는 과일이며 과일 하나를 먹으면 길이가 1만큼 늘어납니다. "
    "과일들은 지상으로부터 일정 높이를 두고 떨어져 있으며 i (1 ≤ i ≤ N) 번째 과일의 높이는 hi입니다. "
    "스네이크버드는 자신의 길이보다 작거나 같은 높이에 있는 과일들을 먹을 수 있습니다."
)

# 파일 내용을 직접 전달하여 요약 상태로 설정
generate_response(user_question, pinecone_data, file_content=file_content)
