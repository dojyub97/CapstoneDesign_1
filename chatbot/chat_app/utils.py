import requests
from django.conf import settings

def query_gemini_api(user_message):
    url = "https://generativelanguage.googleapis.com/v1beta3/models/gemini-1.5:generateText"  # 실제 Google Gemini API 엔드포인트로 변경해야 함
    headers = {
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "prompt": {
            "text": user_message
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        # Extracting response content
        return response.json().get("candidates", [{}])[0].get("output")
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Gemini API: {e}")