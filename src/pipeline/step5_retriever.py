"""STEP 5: Dense + Sparse EnsembleRetriever"""
from typing import List
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever


def build_ensemble_retriever(
    vectorstore: Chroma,
    split_docs: List[Document],
    dense_k: int = 5,
    sparse_k: int = 5,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> EnsembleRetriever:
    """
    Dense(ChromaDB 코사인 유사도) + Sparse(BM25 키워드) 앙상블 리트리버 구성

    - Dense: '부드러운 와인' 같은 의미적 쿼리에 강점
    - Sparse: '탄닌', '지방성', '카베르네' 등 전문 용어 정확 매칭에 강점
    - 기본 가중치: Dense 60% + Sparse 40%
    """
    # Dense Retriever: 벡터 코사인 유사도 기반 시맨틱 검색
    dense_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": dense_k},
    )

    # Sparse Retriever: BM25 키워드 기반 검색
    sparse_retriever = BM25Retriever.from_documents(split_docs)
    sparse_retriever.k = sparse_k

    # Ensemble: Dense + Sparse 가중 결합
    ensemble_retriever = EnsembleRetriever(
        retrievers=[dense_retriever, sparse_retriever],
        weights=[dense_weight, sparse_weight],
    )

    print(
        f"[STEP 5] EnsembleRetriever 구성 완료 "
        f"(Dense {int(dense_weight * 100)}% + Sparse {int(sparse_weight * 100)}%, "
        f"k={dense_k})"
    )
    return ensemble_retriever


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from pipeline.step1_loader import load_documents_from_mysql
    from pipeline.step2_splitter import split_by_metadata
    from pipeline.step3_embedder import get_embeddings
    from pipeline.step4_vectorstore import build_vectorstore

    docs = load_documents_from_mysql()
    split_docs = split_by_metadata(docs)
    embeddings = get_embeddings()
    vectorstore = build_vectorstore(split_docs, embeddings)

    retriever = build_ensemble_retriever(vectorstore, split_docs)

    print("\n[STEP 5] 앙상블 검색 테스트: '카베르네 소비뇽 스테이크'")
    results = retriever.invoke("카베르네 소비뇽 스테이크")
    for r in results:
        print(f"  type={r.metadata.get('type')} | {r.page_content[:100]}...")
