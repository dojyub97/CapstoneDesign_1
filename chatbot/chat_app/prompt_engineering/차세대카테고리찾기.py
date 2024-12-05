import openai
import json
import numpy as np
import faiss
from langchain_openai import OpenAIEmbeddings
import os

# OpenAI API 키 설정
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 임베딩 로드 함수
def load_embeddings(file_path):
    print("임베딩 파일 경로 : ",file_path)
    # 현재 디렉토리 기준으로 경로 생성
    file_path = os.path.join(os.path.dirname(__file__), file_path)
    print("경로 변경 이후 임베딩 파일 경로 : ",file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    texts = [item["text"] for item in data]
    print("여기까지 못오나?1")
    return texts

# # 저장된 FAISS 인덱스를 불러오는 함수
# def load_faiss_index(index_file="faiss_index.bin"):
#     print("인덱스 파일 경로 : ",index_file)
#     # 현재 디렉토리 기준으로 경로 생성
#     index_file = os.path.join(os.path.dirname(__file__), index_file)
#     print("경로 변경 이후 인덱스 파일 경로 : ",index_file)
#     index = faiss.read_index(index_file)
#     print("여기까지 못오나?2")    
#     return index
def load_faiss_index(index_file="faiss_index.bin"):
    try:
        print("인덱스 파일 경로 :", index_file)
        index_file = os.path.join(os.path.dirname(__file__), index_file)
        print("경로 변경 이후 인덱스 파일 경로 :", index_file)
        index = faiss.read_index(index_file)
        print("FAISS 인덱스 로드 성공!")
        return index
    except Exception as e:
        print(f"FAISS 인덱스 로드 실패: {e}")
        raise

# 질문에 가장 유사한 텍스트 검색
def find_most_similar(question, index, texts, embedding_model):
    question_embedding = np.array([embedding_model.embed_query(question)]).astype("float32")
    _, indices = index.search(question_embedding, k=1)
    return texts[indices[0][0]]

# 답변 생성 함수
def generate_answer(question, context):
    prompt = f"질문: {question}\n관련 정보: {context}\n답변:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
                Based on the following table, guide the user to the correct category to find the desired information.
                Only use categories and paths present in the table. If the information is not available, respond with "해당 정보를 찾을 수 없습니다."
                Please respond in KOREAN.
                ex) category1 > category2 > category3
                """
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# RAG 챗봇 함수
def chatbot_rag(question, embeddings_file="embeddings.json", index_file="faiss_index.bin"):
    print("chatbot_rag까지 들어오나?")
    texts = load_embeddings(embeddings_file)
    faiss_index = load_faiss_index(index_file)
    print("임베딩이랑 인덱스 로딩까지 되나?")
    # 질문 임베딩 및 유사도 검색
    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    context = find_most_similar(question, faiss_index, texts, embedding_model)

    # 답변 생성
    answer = generate_answer(question, context)
    return answer