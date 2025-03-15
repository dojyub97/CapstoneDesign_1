from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from .models import EmbeddedText
from .utils import extract_text_from_pdf, generate_embeddings
from .faiss_utils import build_faiss_index, search_faiss_index
from .gpt_utils import gpt로정리

def upload_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES["file"]
        selected_pages = json.loads(request.POST["selected_pages"])

        # PDF 텍스트 추출
        texts = extract_text_from_pdf(pdf_file.temporary_file_path(), selected_pages)

        # 임베딩 생성
        embeddings = generate_embeddings(texts)

        # 데이터베이스 저장
        for item in embeddings:
            EmbeddedText.objects.create(
                page_num=item["page_num"],
                text=item["text"],
                embedding=item["embedding"]
            )

        return JsonResponse({"message": "PDF uploaded and processed."})

def query_chatbot(request):
    if request.method == "POST":
        query = json.loads(request.body)["query"]

        # 질문 임베딩 생성
        query_embedding = generate_embeddings([{"text": query}])[0]["embedding"]

        # 벡터 검색
        all_embeddings = list(EmbeddedText.objects.values("page_num", "text", "embedding"))
        index = build_faiss_index(all_embeddings)
        results = search_faiss_index(query_embedding, index, all_embeddings)

        return JsonResponse({"results": results})


from django.shortcuts import render

def index(request):
    return render(request, "chatbot/index.html")


def fetch_result_content(request):
    if request.method == 'POST':
        # 요청에서 JSON 데이터 파싱
        body = json.loads(request.body)
        result_content = body.get('content', '')

        # 터미널에 출력
        print(f"Received content: {result_content}")

        결과 = gpt로정리(result_content)
        print("================================================")
        print("결과 : ",결과)
        # 응답 반환
        return JsonResponse({'message': 'Result content received successfully!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

