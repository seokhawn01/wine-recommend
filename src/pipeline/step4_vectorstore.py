"""STEP 4: ChromaDB 벡터 저장소"""
import os
from typing import List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
COLLECTION_NAME = "wine_pairing"


def build_vectorstore(split_docs: List[Document], embeddings: OpenAIEmbeddings) -> Chroma:
    """split_docs를 ChromaDB에 저장 후 벡터스토어 반환 (단일 컬렉션, type 필드로 구분)"""
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
    )
    print(f"[STEP 4] ChromaDB 저장 완료 — 컬렉션: {COLLECTION_NAME}, 경로: {CHROMA_PERSIST_DIR}")
    return vectorstore


def load_vectorstore(embeddings: OpenAIEmbeddings) -> Chroma:
    """기존 ChromaDB 로드 (이미 저장된 경우)"""
    vectorstore = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    return vectorstore


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from pipeline.step1_loader import load_documents_from_mysql
    from pipeline.step2_splitter import split_by_metadata
    from pipeline.step3_embedder import get_embeddings

    docs = load_documents_from_mysql()
    split_docs = split_by_metadata(docs)
    embeddings = get_embeddings()
    vectorstore = build_vectorstore(split_docs, embeddings)

    # 저장 확인
    results = vectorstore.similarity_search("카베르네 소비뇽", k=3)
    print(f"\n[STEP 4] 테스트 검색 결과 ({len(results)}개):")
    for r in results:
        print(f"  type={r.metadata.get('type')} | {r.page_content[:80]}...")
