"""STEP 7: ChatOpenAI LLM 연결"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm() -> ChatOpenAI:
    """
    ChatOpenAI 인스턴스 반환

    - model: gpt-4o-mini (빠른 응답 + 충분한 품질)
    - temperature: 0.3 (낮은 온도 → 일관된 전문가 답변)
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    return llm


if __name__ == "__main__":
    llm = get_llm()
    print(f"[STEP 7] LLM 로드 완료 — 모델: {llm.model_name}, temperature: {llm.temperature}")
    # 간단 연결 테스트
    response = llm.invoke("안녕하세요. 한 줄로 답하세요.")
    print(f"[STEP 7] LLM 응답 테스트: {response.content}")
