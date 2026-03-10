"""페어링 쿼리 테스트 — 3가지 시나리오 검증"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "db"))

from main import build_pipeline
from step3_embedder import get_embeddings
from step4_vectorstore import load_vectorstore, build_vectorstore
from step5_retriever import build_ensemble_retriever
from step1_loader import load_documents_from_mysql
from step2_splitter import split_by_metadata


# 테스트 시나리오
QUERIES = [
    # 시나리오 1: 와인으로 메뉴 추천
    "까베르네 소비뇽 와인을 가져갈 건데 어울리는 메뉴 추천해줘",
    # 시나리오 2: 상황 + 와인 복합 쿼리
    "데이트 자리인데, 산미가 강한 화이트 와인에 어울리는 해산물 메뉴 있어?",
    # 시나리오 3: 음식으로 와인 추천 (탄닌 × 매운맛 충돌 확인)
    "매운 한식을 먹을 건데 탄닌 강한 와인 괜찮을까?",
]


def run_tests(chain, show_dense_comparison: bool = True):
    """시나리오별 쿼리 실행 및 결과 출력"""
    print("\n" + "=" * 60)
    print("WinePair 페어링 쿼리 테스트")
    print("=" * 60)

    for i, query in enumerate(QUERIES, 1):
        print(f"\n[시나리오 {i}] {query}")
        print("-" * 60)
        response = chain.invoke(query)
        print(response)

    # Dense 단독 vs Ensemble 비교 (BM25 전문 용어 보완 확인)
    if show_dense_comparison:
        _compare_dense_vs_ensemble()


def _compare_dense_vs_ensemble():
    """Dense 단독 vs Ensemble 검색 결과 비교"""
    print("\n" + "=" * 60)
    print("Dense 단독 vs Ensemble 비교 (BM25 전문 용어 보완 확인)")
    print("=" * 60)

    embeddings = get_embeddings()

    # ChromaDB 로드 (이미 main.py에서 저장됨)
    chroma_dir = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
    if not os.path.exists(chroma_dir):
        print("ChromaDB가 없습니다. main.py를 먼저 실행하세요.")
        return

    vectorstore = load_vectorstore(embeddings)
    docs = load_documents_from_mysql()
    split_docs = split_by_metadata(docs)

    dense_retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    ensemble_retriever = build_ensemble_retriever(vectorstore, split_docs)

    test_query = "탄닌 지방성 페어링"
    print(f"\n테스트 쿼리: '{test_query}'")

    print("\n[Dense 단독 결과]")
    for r in dense_retriever.invoke(test_query):
        print(f"  type={r.metadata.get('type')} | {r.page_content[:80]}...")

    print("\n[Ensemble 결과 (Dense 60% + BM25 40%)]")
    for r in ensemble_retriever.invoke(test_query):
        print(f"  type={r.metadata.get('type')} | {r.page_content[:80]}...")


if __name__ == "__main__":
    chain = build_pipeline()
    run_tests(chain, show_dense_comparison=True)
