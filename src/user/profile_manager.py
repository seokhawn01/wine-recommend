"""사용자 취향 프로파일 CRUD 및 메뉴 필터링 모듈"""
import json
import sys
import os
from dataclasses import dataclass, field
from typing import Optional

# 단독 실행 시 db/ 경로 추가
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "db"))

from sqlalchemy import text


# 식이 제한 키워드 확장 맵
RESTRICTION_KEYWORDS = {
    "해산물": ["해산물", "조개", "새우", "랍스터", "킹크랩", "굴", "오징어", "홍합"],
    "육류":   ["소고기", "돼지고기", "오리", "닭", "스테이크", "갈비", "한우"],
    "유제품": ["치즈", "크림", "버터", "우유", "파르미지아노"],
    "글루텐": ["파스타", "빵", "바게트"],
    "견과류": ["견과류", "아몬드", "호두", "캐슈"],
}


@dataclass
class TasteProfile:
    """사용자 취향 프로파일 데이터클래스"""
    user_id: int
    pref_tannin: float = 2.50
    pref_acidity: float = 2.50
    pref_body: float = 2.50
    pref_sweetness: float = 2.50
    preferred_aromas: list = field(default_factory=list)
    dietary_restrictions: list = field(default_factory=list)

    def to_prompt_text(self) -> str:
        """프롬프트 삽입용 취향 텍스트 생성"""
        lines = [
            "사용자 취향 프로파일:",
            f"  탄닌 {self.pref_tannin:.1f}/5.0 | 산미 {self.pref_acidity:.1f}/5.0"
            f" | 바디감 {self.pref_body:.1f}/5.0 | 당도 {self.pref_sweetness:.1f}/5.0",
        ]
        if self.preferred_aromas:
            lines.append(f"  선호 향: {', '.join(self.preferred_aromas)}")
        if self.dietary_restrictions:
            lines.append(f"  식이 제한: {', '.join(self.dietary_restrictions)}")
        return "\n".join(lines)


def _clamp(value: float, lo: float = 0.0, hi: float = 5.0) -> float:
    """값을 [lo, hi] 범위로 클램핑"""
    return max(lo, min(hi, value))


def _get_engine():
    """connection 모듈에서 엔진 가져오기"""
    try:
        from connection import get_engine
    except ImportError:
        from db.connection import get_engine
    return get_engine()


def get_profile(user_id: int) -> Optional[TasteProfile]:
    """
    취향 프로파일 조회.
    프로파일이 없으면 None 반환.
    """
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT pref_tannin, pref_acidity, pref_body, pref_sweetness,
                       preferred_aromas, dietary_restrictions
                FROM taste_profiles
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        ).fetchone()

    if row is None:
        return None

    aromas = json.loads(row[4]) if row[4] else []
    restrictions = json.loads(row[5]) if row[5] else []

    return TasteProfile(
        user_id=user_id,
        pref_tannin=float(row[0]),
        pref_acidity=float(row[1]),
        pref_body=float(row[2]),
        pref_sweetness=float(row[3]),
        preferred_aromas=aromas,
        dietary_restrictions=restrictions,
    )


def create_profile(user_id: int, profile: TasteProfile) -> None:
    """
    온보딩 시 최초 취향 프로파일 생성.
    이미 존재하면 덮어씀 (REPLACE INTO).
    """
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO taste_profiles
                    (user_id, pref_tannin, pref_acidity, pref_body, pref_sweetness,
                     preferred_aromas, dietary_restrictions)
                VALUES
                    (:uid, :tannin, :acidity, :body, :sweetness, :aromas, :restrictions)
                ON CONFLICT (user_id) DO UPDATE SET
                    pref_tannin = EXCLUDED.pref_tannin,
                    pref_acidity = EXCLUDED.pref_acidity,
                    pref_body = EXCLUDED.pref_body,
                    pref_sweetness = EXCLUDED.pref_sweetness,
                    preferred_aromas = EXCLUDED.preferred_aromas,
                    dietary_restrictions = EXCLUDED.dietary_restrictions
            """),
            {
                "uid": user_id,
                "tannin": profile.pref_tannin,
                "acidity": profile.pref_acidity,
                "body": profile.pref_body,
                "sweetness": profile.pref_sweetness,
                "aromas": json.dumps(profile.preferred_aromas, ensure_ascii=False),
                "restrictions": json.dumps(profile.dietary_restrictions, ensure_ascii=False),
            },
        )
        # 이력 스냅샷 저장
        _save_history(conn, user_id, profile, reason="manual_edit", feedback_id=None)


def update_profile(
    user_id: int,
    tannin_delta: float = 0.0,
    acidity_delta: float = 0.0,
    body_delta: float = 0.0,
    sweetness_delta: float = 0.0,
    reason: str = "feedback",
    feedback_id: Optional[int] = None,
) -> TasteProfile:
    """
    델타값 적용 후 [0.0~5.0] 클램핑.
    변경 후 이력 스냅샷 저장.
    """
    current = get_profile(user_id)
    if current is None:
        # 프로파일 없으면 기본값 생성
        current = TasteProfile(user_id=user_id)
        create_profile(user_id, current)

    new_tannin = _clamp(current.pref_tannin + tannin_delta)
    new_acidity = _clamp(current.pref_acidity + acidity_delta)
    new_body = _clamp(current.pref_body + body_delta)
    new_sweetness = _clamp(current.pref_sweetness + sweetness_delta)

    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE taste_profiles
                SET pref_tannin = :tannin,
                    pref_acidity = :acidity,
                    pref_body = :body,
                    pref_sweetness = :sweetness
                WHERE user_id = :uid
            """),
            {
                "uid": user_id,
                "tannin": new_tannin,
                "acidity": new_acidity,
                "body": new_body,
                "sweetness": new_sweetness,
            },
        )
        updated = TasteProfile(
            user_id=user_id,
            pref_tannin=new_tannin,
            pref_acidity=new_acidity,
            pref_body=new_body,
            pref_sweetness=new_sweetness,
            preferred_aromas=current.preferred_aromas,
            dietary_restrictions=current.dietary_restrictions,
        )
        _save_history(conn, user_id, updated, reason=reason, feedback_id=feedback_id)

    return updated


def get_profile_history(user_id: int, limit: int = 10) -> list[dict]:
    """
    취향 변화 이력 조회 (레이더 차트용).
    최신순 반환.
    """
    engine = _get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT pref_tannin, pref_acidity, pref_body, pref_sweetness,
                       change_reason, created_at
                FROM taste_profile_history
                WHERE user_id = :uid
                ORDER BY created_at DESC
                LIMIT :lim
            """),
            {"uid": user_id, "lim": limit},
        ).fetchall()

    return [
        {
            "pref_tannin": float(r[0]),
            "pref_acidity": float(r[1]),
            "pref_body": float(r[2]),
            "pref_sweetness": float(r[3]),
            "change_reason": r[4],
            "created_at": str(r[5]),
        }
        for r in rows
    ]


def filter_menus_by_restrictions(docs: list, restrictions: list[str]) -> list:
    """
    식이 제한 키워드 기반 메뉴 Document 필터링.
    메뉴 타입 Document 중 제한 식재료가 포함된 항목을 제거.
    와인/식당 Document는 그대로 유지.
    """
    if not restrictions:
        return docs

    # 제한 키워드 집합 구성
    blocked_keywords = set()
    for restriction in restrictions:
        keywords = RESTRICTION_KEYWORDS.get(restriction, [restriction])
        blocked_keywords.update(keywords)

    filtered = []
    for doc in docs:
        doc_type = doc.metadata.get("type", "")
        if doc_type != "menu":
            filtered.append(doc)
            continue

        content = doc.page_content.lower()
        blocked = any(kw.lower() in content for kw in blocked_keywords)
        if not blocked:
            filtered.append(doc)

    return filtered


def _save_history(
    conn,
    user_id: int,
    profile: TasteProfile,
    reason: Optional[str],
    feedback_id: Optional[int],
) -> None:
    """취향 이력 스냅샷 저장 (내부 함수)"""
    conn.execute(
        text("""
            INSERT INTO taste_profile_history
                (user_id, feedback_id, pref_tannin, pref_acidity, pref_body, pref_sweetness,
                 change_reason)
            VALUES
                (:uid, :fid, :tannin, :acidity, :body, :sweetness, :reason)
        """),
        {
            "uid": user_id,
            "fid": feedback_id,
            "tannin": profile.pref_tannin,
            "acidity": profile.pref_acidity,
            "body": profile.pref_body,
            "sweetness": profile.pref_sweetness,
            "reason": reason,
        },
    )


if __name__ == "__main__":
    from connection import get_engine as _
    print("[profile_manager] 모듈 로드 완료")
    print("주요 함수: get_profile, create_profile, update_profile, get_profile_history, filter_menus_by_restrictions")
