from langchain_google_genai import ChatGoogleGenerativeAI
import re
import os
from dotenv import load_dotenv
load_dotenv()
from chat_app.consumers import retrieve_similar_document

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

def print_intro_message(question_type):
    if question_type == "pdf_questions":
        print("PDF 관련 질문 탭입니다. 무엇을 도와드릴까요? 질문해 주세요.")
    elif question_type == "QnA":
        print("예상문제 관련 질문 탭입니다. 예상문제를 생성해 드릴게요. 질문해 주세요.")

def clean_text(document_content):
    document_content = re.sub(r'\s+', ' ', document_content)
    document_content = re.sub(r'[▷-]', '', document_content)
    return document_content.strip()

def format_output(content):
    lines = content.split('. ')
    formatted = '\n'.join(f"- {line.strip()}" for line in lines if line)
    return formatted

base_prompt = {
    "pdf_questions": [
        {
            "role": "assistant",
            "content": (
                "당신은 학생들의 PDF 관련 질문에 친절하고 명확하게 답변하는 선생님입니다. "
                "학생들이 질문하기 편하게 예의를 갖춘 상담원 같은 느낌으로 대해줬으면 좋겠습니다. "
                "학생들이 반말로 질문하면 편하게 반말로 대해주고, ~인가요? 와 같이 존댓말로 질문할 경우 정중하게 존댓말로 대해주세요. "
                "문장에서는 상관없지만 사과와 같은 단어 한개의 출력에 있어 한가지 언어만 사용했으면 좋겠습니다."
                "PDF 파일과 관련된 질문에 대해 요약 요청이나 파일 상태에 대한 안내를 제공해 주세요."
            )
        }
    ],
    "QnA": [
        {
            "role": "assistant",
            "content": (
                "당신은 학생들의 예상문제를 친절하고 명확하게 만들어주는 선생님입니다. "
                "학생들이 질문하기 편하게 예의를 갖춘 상담원 같은 느낌으로 대해줬으면 좋겠습니다. "
                "학생들이 반말로 질문하면 편하게 반말로 대해주고, ~인가요? 와 같이 존댓말로 질문할 경우 정중하게 존댓말로 대해주세요. "
                "문장에서는 상관없지만 사과와 같은 단어 한개의 출력에 있어 한가지 언어만 사용했으면 좋겠습니다."
                "학생들에게 필요한 예상문제를 제공해 주세요. 객관식 문제는 보기와 정답을 포함하고, "
                "주관식 문제는 논술형 답변도 가능합니다."
            )
        }
    ]
}

few_shot_examples = {
    "pdf_questions": [
        {"role": "user", "content": "파일을 요약해 줄 수 있나요?"},
        {"role": "assistant", "content": "먼저 PDF 파일을 업로드해 주세요. 업로드된 파일이 없으면 요약을 진행할 수 없습니다."},
        {"role": "user", "content": "파일 요약을 해주세요."},
        {"role": "assistant", "content": "PDF 파일이 업로드되었다면 최소 5줄, 최대 100줄로 요약해드리겠습니다."},
        {"role": "user", "content": "해당 파일에서 성명을 알고 싶어요."},
        {"role": "assistant", "content": "해당 pdf의 내용에서 성명을 알고 싶으시군요. 이 pdf는 누구의 것입니다."}
    ],
    "QnA": [
        {"role": "user", "content": "수박에 대한 문제를 만들어 주세요."},
        {"role": "assistant", "content": "문제: 수박의 특징에 대해 설명하시오.\n답: 수박은 열대 과일이며 겉이 초록색이고 속이 빨갛습니다."},
        {"role": "user", "content": "객관식 문제를 만들어 주세요."},
        {"role": "assistant", "content": "문제: 다음 중 틀린 것을 고르시오.\na. 수박은 나무에서 자란다.\nb. 수박은 겉이 초록색이다.\nc. 수박은 물을 좋아한다.\nd. 위 내용 중 틀린 것은 하나이다."},
        {"role": "user", "content": "논술형 문제를 만들어 주세요."},
        {"role": "assistant", "content": "문제) 수박의 주요 특징과 생육 환경에 대해 논하시오.\n답: 수박은 열대과일로, 겉이 초록색이고 속은 빨간색이다. 또한, 씨가 있으며 넝쿨에서 자란다.\n수박은 따뜻한 기후에서 잘 자라며, 물이 많은 환경을 선호한다."}
    ]
}

# pdf질문인지 예상문제생성인지 (좀 더 고민할 필요o)
def determine_question_type(user_question):
    if "PDF" in user_question or "파일" in user_question or "요약" in user_question:
        return "pdf_questions"
    return "QnA"

def generate_response(user_question):
    question_type = determine_question_type(user_question)

    selected_prompt = base_prompt[question_type]
    selected_examples = few_shot_examples[question_type]

    print_intro_message(question_type) #터미널에서 확인차 출력

    document_type = "pdf_questions" if question_type == "pdf_questions" else "QnA"
    #document_content, metadata = retrieve_similar_document(user_question, document_type)
    retrieved_documents = retrieve_similar_document(user_question, document_type)

    if isinstance(retrieved_documents, list):
        formatted_chunks = [
            format_output(clean_text(content)) for content, _ in retrieved_documents
        ]
        document_content = "\n\n".join(formatted_chunks)
        metadata = retrieved_documents[0][1] if retrieved_documents else {}
    else:
        document_content, metadata = retrieved_documents

    # 프롬프트 구성
    full_prompt = selected_prompt + selected_examples + [
        {"role": "user", "content": user_question}
    ]

    if (question_type == "pdf_questions" or question_type == "QnA") and not document_content:
        response_content = "파일이 업로드되지 않았습니다. PDF 파일을 먼저 업로드해 주세요."
    else:
        if document_content:
            full_prompt.append({"role": "user", "content": document_content})

    response = llm.invoke(full_prompt)
    response_content = response.content

    final_response = (
        #f"{document_content if document_content else ''}\n"
        f"{response_content}\n"
        f"{metadata['source'] if metadata and 'source' in metadata else '출처 없음'}\n"
    )
    print(final_response)  # 터미널 출력
    return final_response

# test
#with open("C:/Users/easts/OneDrive/바탕 화면/CapstoneDesign_1/김이(010402).pdf", "rb") as pdf_file:
#    add_pdf_to_vector_store(pdf_file)
#
#user_question = "해당 파일에서 어떤 보험 이름이 들어가 있어?"
#generate_response(user_question)


"""
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
        "content": "성명을 알고 싶어요."
    },
    {
        "role": "assistant",
        "content": (
            "해당 pdf의 내용에서 성명을 알고 싶으시군요. 이 pdf는 누구의 것입니다."
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

def generate_response(user_question, context = None, min_lines=5, max_lines=100):
    print_intro_message()

    #pdf_data, _ = retrieve_similar_document(user_question, "pdf_questions")

    # 프롬프트 완성 - 기본 프롬프트 + 예시 + 사용자 질문
    full_prompt = base_prompt + few_shot_examples + [
        {"role": "user", "content": user_question},
    ]

    if not context:
        response_content = "파일이 업로드되지 않았습니다. PDF 파일을 먼저 업로드해 주세요."
    else:
        full_prompt.append({
            "role": "user",
            "content": context
        })

        response = llm.invoke(full_prompt)
        response_content = response.content

    final_response = (
        f"{response_content}"
    )
    print(final_response)  # 터미널 출력
    return final_response

# PDF 파일을 저장하고 테스트
with open("C:/Users/easts/OneDrive/바탕 화면/CapstoneDesign_1/김이(010402).pdf", "rb") as pdf_file:
    add_pdf_to_vector_store(pdf_file)

user_question = "어떤 보험들이 기재되어 있나요?"
context = "이 PDF에는 다양한 보험 상품들이 나열되어 있으며, 그 중 생명보험과 건강보험이 주요 항목으로 기재되어 있습니다."
generate_response(user_question, context = context)"""