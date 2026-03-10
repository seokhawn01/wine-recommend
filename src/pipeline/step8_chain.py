"""STEP 8: LCEL Chain 생성 (기본 + 개인화 체인)"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.retrievers import EnsembleRetriever
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Optional


def _format_docs(docs) -> str:
    """검색된 Document 리스트를 컨텍스트 문자열로 변환"""
    formatted = []
    for i, doc in enumerate(docs, 1):
        doc_type = doc.metadata.get("type", "unknown")
        formatted.append(f"[{i}] ({doc_type})\n{doc.page_content}")
    return "\n\n".join(formatted)


def build_chain(
    ensemble_retriever: EnsembleRetriever,
    prompt: PromptTemplate = None,
    llm: ChatOpenAI = None,
):
    """
    기본 RAG LCEL Chain 생성 (기존 호환 유지).

    흐름: 질문 → 앙상블 리트리버 → 프롬프트 → LLM → 문자열 파싱
    """
    if prompt is None:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from step6_prompt import get_sommelier_prompt
        prompt = get_sommelier_prompt()

    if llm is None:
        from step7_llm import get_llm
        llm = get_llm()

    chain = (
        {
            "context": ensemble_retriever | _format_docs,
            "question": RunnablePassthrough(),
            "user_context": RunnableLambda(lambda _: ""),  # 비로그인 기본값
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("[STEP 8] LCEL Chain 구성 완료")
    return chain


def build_personalized_chain(
    ensemble_retriever: EnsembleRetriever,
    user_id: Optional[int] = None,
    situation: str = "",
    split_docs=None,
    prompt: PromptTemplate = None,
    llm: ChatOpenAI = None,
):
    """
    개인화 RAG Chain 생성.

    사용자 취향 프로파일을 조회하여 프롬프트에 반영하고,
    식이 제한 메뉴를 검색 결과에서 제거합니다.

    Args:
        ensemble_retriever: 앙상블 리트리버 (step5)
        user_id: 로그인 사용자 ID (None이면 비로그인 처리)
        situation: 방문 상황 ("데이트", "친구모임" 등)
        split_docs: 사용하지 않음 (호환성 유지)
        prompt: 프롬프트 템플릿 (None이면 get_sommelier_prompt 사용)
        llm: LLM 인스턴스 (None이면 get_llm 사용)
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))

    if prompt is None:
        from step6_prompt import get_sommelier_prompt, build_user_context
        prompt = get_sommelier_prompt()
    else:
        from step6_prompt import build_user_context

    if llm is None:
        from step7_llm import get_llm
        llm = get_llm()

    # user/ 모듈 import (경로 유연하게 처리)
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from user.profile_manager import get_profile, filter_menus_by_restrictions
    except ImportError:
        from profile_manager import get_profile, filter_menus_by_restrictions

    def _build_inputs(question: str) -> dict:
        """클로저: 질문을 받아 프롬프트 입력 딕셔너리 반환"""
        # 취향 프로파일 조회
        profile = get_profile(user_id) if user_id is not None else None

        # 문서 검색
        docs = ensemble_retriever.invoke(question)

        # 식이 제한 필터
        restrictions = profile.dietary_restrictions if profile else []
        filtered_docs = filter_menus_by_restrictions(docs, restrictions)

        # 사용자 컨텍스트 텍스트 생성
        user_ctx = build_user_context(profile, situation)

        return {
            "context": _format_docs(filtered_docs),
            "question": question,
            "user_context": user_ctx,
        }

    chain = RunnableLambda(_build_inputs) | prompt | llm | StrOutputParser()

    print(f"[STEP 8] 개인화 Chain 구성 완료 (user_id={user_id}, situation='{situation}')")
    return chain


if __name__ == "__main__":
    print("[STEP 8] 단독 실행은 main.py 또는 test_query.py를 사용하세요.")
