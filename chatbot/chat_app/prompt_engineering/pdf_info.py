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

def print_intro_message():
    print("질문을 입력해 주세요. 예상문제 생성 또는 PDF 관련 질문 모두 가능합니다.")

def clean_text(document_content):
    document_content = re.sub(r'\s+', ' ', document_content)
    document_content = re.sub(r'[▷-]', '', document_content)
    return document_content.strip()

def format_output(content):
    lines = content.split('. ')
    formatted = '\n'.join(f"- {line.strip()}" for line in lines if line)
    return formatted

base_prompt = [
    {
        "role": "assistant",
        "content": (
            "당신은 학생들의 질문에 친절하고 명확하게 답변하는 선생님입니다. "
            "학생들이 질문하기 편하게 예의를 갖춘 상담원 같은 느낌으로 대해줬으면 좋겠습니다. "
            "질문 유형에 따라 예상문제를 생성하거나 PDF 파일의 정보를 제공합니다. "
            "문장에서는 상관없지만 사과와 같은 단어 한개의 출력에 있어 한가지 언어만 사용했으면 좋겠습니다. "
            "학생들이 반말로 질문하면 편하게 반말로 대해주고, 존댓말로 질문할 경우 정중하게 존댓말로 답해주세요. "
            "PDF 파일과 관련된 요청에서는 파일 상태나 요약을 제공하고, 예상문제 요청에서는 객관식 및 주관식 혹은 논술형 문제를 생성하세요."
        )
    }
]

few_shot_examples = [
    {"role": "user", "content": "파일을 요약해 줄 수 있나요?"},
    {"role": "assistant", "content": "먼저 PDF 파일을 업로드해 주세요. 업로드된 파일이 없으면 요약을 진행할 수 없습니다."},
    {"role": "user", "content": "파일 요약을 해주세요."},
    {"role": "assistant", "content": "PDF 파일이 업로드되었다면 최소 5줄, 최대 100줄로 요약해드리겠습니다."},
    {"role": "user", "content": "해당 파일에서 성명을 알고 싶어요."},
    {"role": "assistant", "content": "해당 pdf의 내용에서 성명을 알고 싶으시군요. 이 pdf는 누구의 것입니다."},
    {"role": "user", "content": "수박에 대한 문제를 만들어 주세요."},
    {"role": "assistant", "content": "문제: 수박의 특징에 대해 설명하시오.\n답: 수박은 열대 과일이며 겉이 초록색이고 속이 빨갛습니다."},
    {"role": "user", "content": "객관식 문제를 만들어 주세요."},
    {"role": "assistant", "content": "문제: 다음 중 틀린 것을 고르시오.\na. 수박은 나무에서 자란다.\nb. 수박은 겉이 초록색이다.\nc. 수박은 물을 좋아한다.\nd. 위 내용 중 틀린 것은 하나이다."},
    {"role": "user", "content": "논술형 문제를 만들어 주세요."},
    {"role": "assistant", "content": "문제) 수박의 주요 특징과 생육 환경에 대해 논하시오.\n답: 수박은 열대과일로, 겉이 초록색이고 속은 빨간색이다. 또한, 씨가 있으며 넝쿨에서 자란다.\n수박은 따뜻한 기후에서 잘 자라며, 물이 많은 환경을 선호한다."}
]

def generate_response(user_question, class_material):
    print_intro_message()

    document_type = "textbook"
    retrieved_documents = retrieve_similar_document(class_material, document_type)

    if isinstance(retrieved_documents, list):
        formatted_chunks = [
            format_output(clean_text(doc.page_content)) for doc in retrieved_documents
        ]
        document_content = "\n\n".join(formatted_chunks)
        metadata = retrieved_documents[0].metadata if retrieved_documents else {}
    else:
        document_content, metadata = retrieved_documents

    if not document_content:
        response_content = "파일이 업로드되지 않았습니다. PDF 파일을 먼저 업로드해 주세요."
    else:
        full_prompt = base_prompt + few_shot_examples + [
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": document_content}
        ]
        response = llm.invoke(full_prompt)
        response_content = response.content

    final_response = (
        f"{response_content}\n"
    )

    print(final_response)  # 터미널에 응답 출력
    return final_response

# test
# user_question = "운영체제의 목차에 대해 알고싶어."
# class_material = "이 파일에는 운영체제에 관한 내용이 들어가 있습니다."
# generate_response(user_question, class_material)


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