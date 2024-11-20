from langchain.chat_models import ChatOpenAI

import os
openai_api_key=os.environ["OPENAI_API_KEY"]  #openai 키 입력

def gpt로정리(input_text):  #llm이 답변 생성

    # 다음은 수업 ppt자료의 일부인데, 다음 내용에 대해서 자세히 설명해줘.

    prompt=f"""
    다음은 수업 ppt자료의 일부인데, 다음 내용을 정리해줘.
    ================================================================\n\n
    """+input_text

    llm = ChatOpenAI(temperature=0,  # 창의성 0으로 설정 
                 model_name='gpt-4o-mini',  # 모델명
                 openai_api_key=openai_api_key
                )
    return (llm.invoke(prompt))