import requests
from django.conf import settings

def query_gemini_api(user_message):
    url = "https://api.example.com/gemini"  # 실제 Google Gemini API 엔드포인트로 변경해야 함
    headers = {
        "Authorization": f"Bearer {settings.GOOGLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "query": user_message,
        # 필요에 따라 추가 데이터
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.json()  # JSON 응답 반환
    except requests.exceptions.RequestException as e:
        # 로깅 또는 오류 처리
        print(f"Error querying Google Gemini API: {e}")
        return None