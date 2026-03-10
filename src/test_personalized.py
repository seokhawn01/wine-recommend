"""
개인화 취향 시스템 통합 테스트
사전 조건: main.py 실행 완료 + chroma_db/ 존재
실행: cd src && python test_personalized.py
"""
import sys
import os

# 모듈 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "db"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "user"))
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from connection import get_engine
from profile_manager import (
    TasteProfile,
    create_profile,
    get_profile,
    update_profile,
    get_profile_history,
    filter_menus_by_restrictions,
)
from feedback_processor import analyze_review_with_gpt, save_feedback
from sqlalchemy import text


# ── 테스트용 사용자 생성 헬퍼 ─────────────────────────────────────────────────

def _create_test_user(email: str = "test_personal@winepair.io") -> int:
    """테스트 사용자 upsert 후 user_id 반환"""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO users (email, password_hash, nickname, onboarding_done)
                VALUES (:email, 'hashed_pw', '테스트유저', TRUE)
                ON DUPLICATE KEY UPDATE nickname = VALUES(nickname)
            """),
            {"email": email},
        )
        row = conn.execute(
            text("SELECT user_id FROM users WHERE email = :email"),
            {"email": email},
        ).fetchone()
    return row[0]


def _get_first_wine_id() -> int:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT wine_id FROM wines LIMIT 1")).fetchone()
    if row is None:
        raise RuntimeError("wines 테이블에 데이터가 없습니다. seed_data.py를 먼저 실행하세요.")
    return row[0]


def _get_first_menu_id() -> int:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT menu_id FROM menus LIMIT 1")).fetchone()
    if row is None:
        raise RuntimeError("menus 테이블에 데이터가 없습니다. seed_data.py를 먼저 실행하세요.")
    return row[0]


def _get_first_restaurant_id() -> int:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT restaurant_id FROM restaurants LIMIT 1")).fetchone()
    if row is None:
        raise RuntimeError("restaurants 테이블에 데이터가 없습니다. seed_data.py를 먼저 실행하세요.")
    return row[0]


# ── 테스트 함수 ───────────────────────────────────────────────────────────────

def test_01_profile_crud():
    """취향 프로파일 생성·조회·값 검증"""
    print("\n[TEST 01] 취향 프로파일 생성·조회 테스트")
    user_id = _create_test_user()

    profile = TasteProfile(
        user_id=user_id,
        pref_tannin=3.5,
        pref_acidity=4.0,
        pref_body=3.0,
        pref_sweetness=1.5,
        preferred_aromas=["과일", "오크"],
        dietary_restrictions=["해산물", "견과류"],
    )
    create_profile(user_id, profile)

    loaded = get_profile(user_id)
    assert loaded is not None, "프로파일 조회 실패"
    assert abs(loaded.pref_tannin - 3.5) < 0.01, f"탄닌 불일치: {loaded.pref_tannin}"
    assert abs(loaded.pref_acidity - 4.0) < 0.01, f"산미 불일치: {loaded.pref_acidity}"
    assert "해산물" in loaded.dietary_restrictions, "식이 제한 불일치"

    prompt_text = loaded.to_prompt_text()
    assert "탄닌" in prompt_text, "프롬프트 텍스트 생성 실패"

    print(f"  user_id={user_id}")
    print(f"  프로파일: {prompt_text}")
    print("  ✓ TEST 01 통과\n")
    return user_id


def test_02_personalized_query(user_id: int):
    """개인화 쿼리 실행 및 해산물 제외 필터 검증"""
    print("[TEST 02] 개인화 쿼리 + 식이 제한 필터 테스트")

    from langchain.schema import Document

    # 테스트용 Document 목록 (해산물 포함/미포함)
    test_docs = [
        Document(page_content="메뉴: 킹크랩 찜", metadata={"type": "menu"}),
        Document(page_content="메뉴: 한우 스테이크", metadata={"type": "menu"}),
        Document(page_content="와인: 카베르네 소비뇽", metadata={"type": "wine"}),
        Document(page_content="메뉴: 파스타 크림소스", metadata={"type": "menu"}),
        Document(page_content="메뉴: 리조또", metadata={"type": "menu"}),
    ]

    profile = get_profile(user_id)
    restrictions = profile.dietary_restrictions  # ["해산물", "견과류"]
    filtered = filter_menus_by_restrictions(test_docs, restrictions)

    # 킹크랩(해산물)은 제외, 한우·와인·파스타·리조또는 유지
    contents = [d.page_content for d in filtered]
    assert not any("킹크랩" in c for c in contents), "해산물 필터 미작동"
    assert any("한우" in c for c in contents), "한우가 잘못 필터링됨"
    assert any("카베르네" in c for c in contents), "와인 Document가 잘못 필터링됨"

    print(f"  원본 문서 수: {len(test_docs)}, 필터 후: {len(filtered)}")
    print(f"  잔여 문서: {[d.page_content[:20] for d in filtered]}")
    print("  ✓ TEST 02 통과\n")


def test_03_feedback_and_update(user_id: int):
    """피드백 저장 → GPT 분석 → 탄닌 벡터 변화 검증"""
    print("[TEST 03] 피드백 저장 + 취향 업데이트 테스트")

    wine_id = _get_first_wine_id()
    menu_id = _get_first_menu_id()
    restaurant_id = _get_first_restaurant_id()

    before = get_profile(user_id)
    print(f"  업데이트 전 탄닌: {before.pref_tannin}")

    # 탄닌이 강해서 별로였다는 리뷰 (탄닌 감소 유도)
    review = "탄닌이 너무 강해서 음식과 잘 안 어울렸어요. 떫은 맛이 너무 강합니다."
    feedback_id = save_feedback(
        user_id=user_id,
        wine_id=wine_id,
        menu_id=menu_id,
        restaurant_id=restaurant_id,
        reaction=-1,
        review_text=review,
        situation="친구모임",
    )

    after = get_profile(user_id)
    print(f"  업데이트 후 탄닌: {after.pref_tannin}")
    print(f"  feedback_id: {feedback_id}")

    assert feedback_id > 0, "feedback_id 반환 실패"
    # 탄닌이 감소하거나 동일해야 함 (GPT 또는 reaction 기반 처리)
    assert after.pref_tannin <= before.pref_tannin + 0.01, \
        f"탄닌이 증가함 ({before.pref_tannin} → {after.pref_tannin})"

    print("  ✓ TEST 03 통과\n")
    return feedback_id


def test_04_profile_history(user_id: int):
    """취향 변화 이력 조회 (1개 이상 확인)"""
    print("[TEST 04] 취향 변화 이력 조회 테스트")

    history = get_profile_history(user_id, limit=10)
    assert len(history) >= 1, f"이력이 없음 (len={len(history)})"

    print(f"  이력 수: {len(history)}")
    for h in history[:3]:
        print(f"    [{h['created_at']}] 탄닌={h['pref_tannin']:.2f} / 사유={h['change_reason']}")

    print("  ✓ TEST 04 통과\n")


def test_05_gpt_structured_output():
    """GPT Structured Output 단독 테스트 (2개 케이스)"""
    print("[TEST 05] GPT Structured Output 단독 테스트")

    wine_id = _get_first_wine_id()

    cases = [
        {
            "review": "탄닌이 너무 강하고 텁텁해서 별로였어요. 다음엔 가벼운 와인을 마시고 싶어요.",
            "expected_sentiment": "negative",
        },
        {
            "review": "산미가 적당하고 부드러워서 음식과 아주 잘 어울렸습니다. 다시 주문하고 싶어요!",
            "expected_sentiment": "positive",
        },
    ]

    for i, case in enumerate(cases, 1):
        adj = analyze_review_with_gpt(case["review"], wine_id)
        print(f"  케이스 {i}: sentiment={adj.sentiment}, confidence={adj.confidence:.2f}")
        print(f"    delta: 탄닌={adj.tannin_delta:+.2f}, 산미={adj.acidity_delta:+.2f}")
        print(f"    key_signals: {adj.key_signals}")

        assert adj.sentiment in ("positive", "negative", "neutral"), \
            f"sentiment 범위 오류: {adj.sentiment}"
        assert 0.0 <= adj.confidence <= 1.0, \
            f"confidence 범위 오류: {adj.confidence}"
        assert -1.0 <= adj.tannin_delta <= 1.0, \
            f"tannin_delta 범위 오류: {adj.tannin_delta}"

    print("  ✓ TEST 05 통과\n")


# ── 테스트 러너 ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("WinePair 개인화 취향 시스템 통합 테스트")
    print("=" * 60)

    passed = 0
    failed = 0

    tests = [
        ("TEST 01: 프로파일 CRUD",    lambda: test_01_profile_crud()),
        ("TEST 02: 개인화 쿼리 필터", None),  # user_id 필요 — 아래에서 순서대로 실행
        ("TEST 03: 피드백 업데이트",  None),
        ("TEST 04: 이력 조회",        None),
        ("TEST 05: GPT 구조화 출력",  lambda: test_05_gpt_structured_output()),
    ]

    # 순서 의존성이 있는 테스트는 직접 실행
    try:
        user_id = test_01_profile_crud()
        passed += 1
    except Exception as e:
        print(f"  ✗ TEST 01 실패: {e}\n")
        failed += 1
        user_id = None

    try:
        if user_id:
            test_02_personalized_query(user_id)
            passed += 1
    except Exception as e:
        print(f"  ✗ TEST 02 실패: {e}\n")
        failed += 1

    try:
        if user_id:
            test_03_feedback_and_update(user_id)
            passed += 1
    except Exception as e:
        print(f"  ✗ TEST 03 실패: {e}\n")
        failed += 1

    try:
        if user_id:
            test_04_profile_history(user_id)
            passed += 1
    except Exception as e:
        print(f"  ✗ TEST 04 실패: {e}\n")
        failed += 1

    try:
        test_05_gpt_structured_output()
        passed += 1
    except Exception as e:
        print(f"  ✗ TEST 05 실패: {e}\n")
        failed += 1

    print("=" * 60)
    print(f"결과: {passed}개 통과 / {failed}개 실패 / 총 5개")
    print("=" * 60)
