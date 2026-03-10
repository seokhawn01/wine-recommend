"""WinePair LangChain 8단계 RAG 파이프라인 전체 실행"""
import sys
import os
from dotenv import load_dotenv

# LangSmith 트레이싱을 위해 환경변수 최우선 로드
load_dotenv()

# 모듈 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "db"))

from step1_loader import load_documents_from_mysql
from step2_splitter import split_by_metadata
from step3_embedder import get_embeddings
from step4_vectorstore import build_vectorstore
from step5_retriever import build_ensemble_retriever
from step6_prompt import get_sommelier_prompt
from step7_llm import get_llm
from step8_chain import build_chain


def build_pipeline():
    """8단계 파이프라인 구축 후 chain 반환"""
    print("=" * 50)
    print("WinePair RAG 파이프라인 시작")
    print("=" * 50)

    # STEP 1: MySQL → Document 로드
    docs = load_documents_from_mysql()
    print(f"  로드된 문서 수: {len(docs)}")

    # STEP 2: metadata 기준 청크 분할
    split_docs = split_by_metadata(docs)
    print(f"  분할된 청크 수: {len(split_docs)}")

    # STEP 3: 임베딩 모델 준비
    embeddings = get_embeddings()
    print("  임베딩 모델 준비 완료 (text-embedding-3-small)")

    # STEP 4: ChromaDB 저장
    vectorstore = build_vectorstore(split_docs, embeddings)

    # STEP 5: Dense + Sparse 앙상블 리트리버
    ensemble_retriever = build_ensemble_retriever(vectorstore, split_docs)

    # STEP 6: 소믈리에 프롬프트
    prompt = get_sommelier_prompt()
    print("  프롬프트 템플릿 준비 완료")

    # STEP 7: LLM 연결
    llm = get_llm()
    print(f"  LLM 준비 완료 ({llm.model_name})")

    # STEP 8: LCEL Chain 생성
    chain = build_chain(ensemble_retriever, prompt, llm)

    print("=" * 50)
    print("파이프라인 구축 완료!")
    print("=" * 50)

    return chain


if __name__ == "__main__":
    chain = build_pipeline()

    # 기본 동작 확인 쿼리
    print("\n[테스트 쿼리] 카베르네 소비뇽 와인에 어울리는 메뉴를 추천해줘")
    print("-" * 50)
    response = chain.invoke("카베르네 소비뇽 와인에 어울리는 메뉴를 추천해줘")
    print(response)
