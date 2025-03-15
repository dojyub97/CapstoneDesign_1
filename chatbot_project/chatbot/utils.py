import fitz  # PyMuPDF
import openai

# OpenAI API 키 설정
openai.api_key = os.environ["OPENAI_API_KEY"]

def extract_text_from_pdf(file_path, selected_pages):
    pdf = fitz.open(file_path)
    page_texts = []
    for page_num in selected_pages:
        page = pdf[page_num - 1]  # 페이지는 0부터 시작
        text = page.get_text()
        page_texts.append({"page_num": page_num, "text": text})
    pdf.close()
    return page_texts

def generate_embeddings(texts):
    embeddings = []
    for item in texts:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=item["text"]
        )
        embeddings.append({
            "page_num": item["page_num"],
            "embedding": response["data"][0]["embedding"],
            "text": item["text"]
        })
    return embeddings
