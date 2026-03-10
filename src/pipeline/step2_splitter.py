"""STEP 2: metadata type 기준 청크 분할"""
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# type별 청크 설정
CHUNK_CONFIG = {
    "wine":       {"chunk_size": 400, "chunk_overlap": 40},
    "menu":       {"chunk_size": 300, "chunk_overlap": 30},
    "restaurant": {"chunk_size": 250, "chunk_overlap": 25},
}

# 파이프 구분자 우선 보존 (SQL 레코드 구조 유지)
SEPARATORS = ["\n\n", "\n", " | ", " ", ""]


def split_by_metadata(docs: List[Document]) -> List[Document]:
    """metadata type 기준으로 docs를 분리 후 각각 다른 splitter 적용"""
    # type별로 문서 분류
    grouped: dict[str, List[Document]] = {"wine": [], "menu": [], "restaurant": []}
    for doc in docs:
        doc_type = doc.metadata.get("type", "wine")
        grouped.setdefault(doc_type, []).append(doc)

    split_docs: List[Document] = []
    for doc_type, type_docs in grouped.items():
        if not type_docs:
            continue
        config = CHUNK_CONFIG.get(doc_type, CHUNK_CONFIG["wine"])
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            separators=SEPARATORS,
        )
        chunks = splitter.split_documents(type_docs)
        # 분할 후 자식 chunk에도 원본 metadata 유지 (splitter가 자동 상속)
        split_docs.extend(chunks)
        print(f"[STEP 2] {doc_type}: {len(type_docs)}개 문서 → {len(chunks)}개 청크")

    print(f"[STEP 2] 총 청크 수: {len(split_docs)}")
    return split_docs


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pipeline"))
    from step1_loader import load_documents_from_mysql

    docs = load_documents_from_mysql()
    split_docs = split_by_metadata(docs)
    print("\n--- 분할된 청크 예시 ---")
    for doc in split_docs[:3]:
        print(f"type={doc.metadata.get('type')} | len={len(doc.page_content)}")
        print(doc.page_content[:120], "...")
        print()
