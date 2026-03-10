"""STEP 1: MySQL → LangChain Document 변환 (구조적 텍스트)"""
from typing import List
from langchain_core.documents import Document
from sqlalchemy import text

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "db"))
from connection import get_engine


def _load_wines(conn) -> List[Document]:
    """wines 테이블 → Document 리스트"""
    rows = conn.execute(text("SELECT * FROM wines ORDER BY wine_id")).fetchall()
    docs = []
    for row in rows:
        vintage_str = str(row.vintage) if row.vintage else "NV"
        content = (
            f"와인명: {row.name} | 품종: {row.grape_variety} | 지역: {row.region} | 빈티지: {vintage_str}\n"
            f"타입: {row.wine_type} | 탄닌: {row.tannin} | 산미: {row.acidity} | "
            f"바디감: {row.body} | 당도: {row.sweetness}\n"
            f"향: {row.aroma or '정보 없음'}\n"
            f"설명: {row.description or ''}"
        )
        metadata = {
            "type": "wine",
            "wine_id": row.wine_id,
            "grape_variety": row.grape_variety,
            "wine_type": row.wine_type,
            "tannin": float(row.tannin),
            "acidity": float(row.acidity),
            "body": float(row.body),
            "sweetness": float(row.sweetness),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def _load_menus(conn) -> List[Document]:
    """menus 테이블 → Document 리스트 (식당명 JOIN)"""
    rows = conn.execute(
        text("""
            SELECT m.*, r.name AS restaurant_name, r.food_category
            FROM menus m
            JOIN restaurants r ON m.restaurant_id = r.restaurant_id
            ORDER BY m.menu_id
        """)
    ).fetchall()
    docs = []
    for row in rows:
        content = (
            f"메뉴명: {row.name} | 카테고리: {row.category} | 가격: {row.price}원 | 식당: {row.restaurant_name}\n"
            f"음식 장르: {row.food_category}\n"
            f"지방성: {row.fattiness} | 감칠맛: {row.umami} | 매운맛: {row.spiciness} | "
            f"단맛: {row.sweetness} | 산미: {row.acidity}\n"
            f"설명: {row.description or ''}"
        )
        metadata = {
            "type": "menu",
            "menu_id": row.menu_id,
            "restaurant_id": row.restaurant_id,
            "restaurant_name": row.restaurant_name,
            "category": row.category,
            "price": row.price,
            "fattiness": float(row.fattiness),
            "umami": float(row.umami),
            "spiciness": float(row.spiciness),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def _load_restaurants(conn) -> List[Document]:
    """restaurants 테이블 → Document 리스트"""
    rows = conn.execute(text("SELECT * FROM restaurants ORDER BY restaurant_id")).fetchall()
    docs = []
    for row in rows:
        reservation_str = "예약 필수" if row.reservation_required else "예약 불필요"
        content = (
            f"식당명: {row.name} | 카테고리: {row.food_category} | 주소: {row.address}\n"
            f"콜키지: {row.corkage_fee}원/병 | 최대 {row.corkage_limit}병 | {reservation_str} | "
            f"별점: {row.rating}"
        )
        metadata = {
            "type": "restaurant",
            "restaurant_id": row.restaurant_id,
            "food_category": row.food_category,
            "corkage_fee": row.corkage_fee,
            "rating": float(row.rating),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def load_documents_from_mysql() -> List[Document]:
    """MySQL 전체 테이블에서 LangChain Document 로드"""
    engine = get_engine()
    with engine.connect() as conn:
        wine_docs = _load_wines(conn)
        menu_docs = _load_menus(conn)
        restaurant_docs = _load_restaurants(conn)

    all_docs = wine_docs + menu_docs + restaurant_docs
    print(f"[STEP 1] 로드 완료 — 와인: {len(wine_docs)}, 메뉴: {len(menu_docs)}, 식당: {len(restaurant_docs)}")
    return all_docs


if __name__ == "__main__":
    docs = load_documents_from_mysql()
    print(f"\n총 문서 수: {len(docs)}")
    print("\n--- 첫 번째 문서 예시 ---")
    print(docs[0].page_content)
    print(docs[0].metadata)
