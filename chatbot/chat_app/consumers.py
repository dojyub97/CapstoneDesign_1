import json
from .prompt_engineering import general_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from uuid import uuid4
import time
import fitz

index_name = "langchain-test-index"
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

# index 삭제하는 함수  
def delete_index(index_name):
    if index_name in [index_info["name"] for index_info in pc.list_indexes()]:
        pc.delete_index(index_name)
        return f"Index '{index_name}' has been deleted."
    return f"Index '{index_name}' does not exist."

# 인덱스 생성 함수
# index = create_index() 이렇게 호출
def create_index(index_name="langchain-test-index", dimension=768):
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)
    return pc.Index(index_name)

# 쿼리 및 검색 함수
def retrieve_similar_document(query, query_type):
    # query는 문자열
    # query_type은 "school_life", "pdf_questions", "QnA" 중 하나일 것.
    # retrieve_simiilar_documents("2024년 2학기 장학금",  "school_info")
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                                    google_api_key=GEMINI_API_KEY)
    index = create_index()
    vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)
    result = vector_store.similarity_search(query, k=1, filter={"type": query_type}) 
    return (result[0].page_content, result[0].metadata)
    # result[0].page_content는 db에 저장돼있던 데이터본문에 해당. 
    # result[0].metadata는 데이터본문의 메타데이터로 딕셔너리 구조. 

#pdf->document->chunk->vdb
def PdfToDocument(pdf_file):
    pdf_text = ""
    # PDF 파일 내용을 읽고 텍스트로 변환
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf:
        for page in pdf:
            pdf_text += page.get_text()

    # Document 객체 생성
    document = Document(
        page_content=pdf_text,
        metadata={
            "source": pdf_file.name,      
            "type": "pdf_questions",                
            "title": pdf_file.name
        }
    )
    return document

def DocumentToChunks(document):
# 청크화된 문서를 저장할 리스트
    chunks = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap  = 100,
        length_function = len,
    )

    
    split_texts = text_splitter.split_text(document.page_content)
    for i, chunk_text in enumerate(split_texts):
        chunk_metadata = document.metadata.copy()  # 원본 metadata 복사
        chunk_metadata["chunknum"] = i + 1  # chunknum 추가
        
        chunk_document = Document(
            page_content=chunk_text,
            metadata=chunk_metadata
        )
        chunks.append(chunk_document)
    
    return chunks         
def add_documents_to_vector_store(documents):
    # 벡터 DB에 Document객체 저장
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                                    google_api_key=GEMINI_API_KEY)
    index = create_index()
    vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    return "Documents added to vector store."

def add_pdf_to_vector_store(pdf_file):
    document = PdfToDocument(pdf_file)
    chunks = DocumentToChunks(document)
    add_documents_to_vector_store(chunks)