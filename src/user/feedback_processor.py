"""피드백 저장 및 GPT Structured Output 기반 취향 학습 모듈"""
import json
import os
import sys
from typing import Optional

from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

# 단독 실행 시 경로 추가
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "db"))
    sys.path.insert(0, os.path.dirname(__file__))

try:
    from connection import get_engine
    from profile_manager import get_profile, update_profile, TasteProfile, create_profile
except ImportError:
    from db.connection import get_engine
    from user.profile_manager import get_profile, update_profile, TasteProfile, create_profile

from sqlalchemy import text


# ── GPT Structured Output 스키마 ──────────────────────────────────────────────

class TasteAdjustment(BaseModel):
    """GPT가 리뷰 텍스트를 분석해 반환하는 취향 조정 구조체"""
    tannin_delta: float       # -1.0 ~ +1.0
    acidity_delta: float      # -1.0 ~ +1.0
    body_delta: float         # -1.0 ~ +1.0
    sweetness_delta: float    # -1.0 ~ +1.0
    sentiment: str            # "positive" | "negative" | "neutral"
    key_signals: list[str]    # 조정 근거 텍스트 (디버깅용)
    confidence: float         # 0.0~1.0, 0.5 미만이면 업데이트 보류


# ── 내부 헬퍼 ─────────────────────────────────────────────────────────────────

def _get_wine_attrs(wine_id: int) -> dict:
    """와인의 탄닌/산미/바디/당도 조회"""
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT tannin, acidity, body, sweetness FROM wines WHERE wine_id = :wid"),
            {"wid": wine_id},
        ).fetchone()
    if row is None:
        return {"tannin": 2.5, "acidity": 2.5, "body": 2.5, "sweetness": 2.5}
    return {
        "tannin": float(row[0]),
        "acidity": float(row[1]),
        "body": float(row[2]),
        "sweetness": float(row[3]),
    }


@traceable(name="analyze_review_with_gpt", run_type="llm")
def analyze_review_with_gpt(review_text: str, wine_id: int) -> TasteAdjustment:
    """
    GPT-4o-mini Structured Output으로 리뷰 텍스트 분석.
    와인 속성을 컨텍스트로 제공해 더 정확한 델타 계산.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    wine_attrs = _get_wine_attrs(wine_id)

    system_prompt = (
        "당신은 와인 취향 분석 전문가입니다. "
        "사용자의 와인 리뷰를 분석하여 취향 벡터(탄닌/산미/바디감/당도)의 조정값을 JSON으로 반환합니다.\n"
        "조정값 범위: -1.0 ~ +1.0 (긍정 후기=해당 특성 선호도 상승, 부정 후기=하락)\n"
        "confidence가 0.5 미만이면 리뷰가 불명확한 것으로 판단합니다."
    )

    user_prompt = (
        f"[와인 속성] 탄닌={wine_attrs['tannin']}, 산미={wine_attrs['acidity']}, "
        f"바디감={wine_attrs['body']}, 당도={wine_attrs['sweetness']}\n\n"
        f"[사용자 리뷰]\n{review_text}"
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=TasteAdjustment,
        temperature=0.2,
    )

    return completion.choices[0].message.parsed


def _apply_reaction_only_delta(
    user_id: int,
    wine_id: int,
    reaction: int,
    feedback_id: int,
) -> None:
    """
    텍스트 후기 없이 좋아요/별로만 있을 때 소폭 delta 적용.
    와인 특성값과 현재 취향의 차이가 0.5 초과인 차원에만 ±0.1 적용.
    """
    if reaction == 0:
        return

    profile = get_profile(user_id)
    if profile is None:
        return

    wine = _get_wine_attrs(wine_id)
    sign = 1 if reaction == 1 else -1  # 좋아요=+, 별로=-
    delta = 0.1 * sign

    tannin_delta = delta if abs(wine["tannin"] - profile.pref_tannin) > 0.5 else 0.0
    acidity_delta = delta if abs(wine["acidity"] - profile.pref_acidity) > 0.5 else 0.0
    body_delta = delta if abs(wine["body"] - profile.pref_body) > 0.5 else 0.0
    sweetness_delta = delta if abs(wine["sweetness"] - profile.pref_sweetness) > 0.5 else 0.0

    reason = "feedback_good_reaction" if reaction == 1 else "feedback_bad_reaction"
    update_profile(
        user_id=user_id,
        tannin_delta=tannin_delta,
        acidity_delta=acidity_delta,
        body_delta=body_delta,
        sweetness_delta=sweetness_delta,
        reason=reason,
        feedback_id=feedback_id,
    )


# ── 공개 함수 ─────────────────────────────────────────────────────────────────

@traceable(name="save_feedback", run_type="chain")
def save_feedback(
    user_id: int,
    wine_id: int,
    menu_id: int,
    restaurant_id: int,
    reaction: int = 0,
    review_text: str = "",
    situation: str = "",
) -> int:
    """
    피드백 저장 + 취향 업데이트 파이프라인.

    처리 흐름:
    1. feedbacks INSERT (applied=False)
    2. review_text >= 5자 → GPT 분석 → profile_adjustments 저장
    3-a. confidence >= 0.5: GPT delta × confidence 가중치로 update_profile
    3-b. 텍스트 없음 또는 confidence < 0.5: reaction 기반 소폭 delta
    4. feedbacks.applied = True

    반환: feedback_id
    """
    engine = get_engine()
    feedback_id: Optional[int] = None

    with engine.begin() as conn:
        # 1. feedbacks INSERT (RETURNING으로 생성된 ID 수집)
        result = conn.execute(
            text("""
                INSERT INTO feedbacks
                    (user_id, wine_id, menu_id, restaurant_id, situation, reaction, review_text)
                VALUES
                    (:uid, :wid, :mid, :rid, :sit, :react, :review)
                RETURNING feedback_id
            """),
            {
                "uid": user_id,
                "wid": wine_id,
                "mid": menu_id,
                "rid": restaurant_id,
                "sit": situation or None,
                "react": reaction,
                "review": review_text or None,
            },
        )
        feedback_id = result.fetchone()[0]

    # 2. GPT 분석 (트랜잭션 외부 — API 호출 시간 분리)
    gpt_applied = False
    adjustment: Optional[TasteAdjustment] = None

    if review_text and len(review_text.strip()) >= 5:
        try:
            adjustment = analyze_review_with_gpt(review_text, wine_id)
            adj_json = adjustment.model_dump_json()

            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE feedbacks
                        SET profile_adjustments = :adj
                        WHERE feedback_id = :fid
                    """),
                    {"adj": adj_json, "fid": feedback_id},
                )

            # 3-a. confidence >= 0.5: GPT delta 적용
            if adjustment.confidence >= 0.5:
                w = adjustment.confidence  # 가중치
                reason = "feedback_good_gpt" if adjustment.sentiment == "positive" else "feedback_bad_gpt"
                update_profile(
                    user_id=user_id,
                    tannin_delta=adjustment.tannin_delta * w,
                    acidity_delta=adjustment.acidity_delta * w,
                    body_delta=adjustment.body_delta * w,
                    sweetness_delta=adjustment.sweetness_delta * w,
                    reason=reason,
                    feedback_id=feedback_id,
                )
                gpt_applied = True

        except Exception as e:
            print(f"[feedback_processor] GPT 분석 실패: {e}")

    # 3-b. GPT 미적용 시 reaction 기반 소폭 delta
    if not gpt_applied:
        _apply_reaction_only_delta(
            user_id=user_id,
            wine_id=wine_id,
            reaction=reaction,
            feedback_id=feedback_id,
        )

    # 4. applied = True
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE feedbacks SET applied = TRUE WHERE feedback_id = :fid"),
            {"fid": feedback_id},
        )

    print(f"[feedback_processor] 피드백 #{feedback_id} 저장 완료 (gpt_applied={gpt_applied})")
    return feedback_id


if __name__ == "__main__":
    print("[feedback_processor] 모듈 로드 완료")
    print("주요 함수: save_feedback, analyze_review_with_gpt")
