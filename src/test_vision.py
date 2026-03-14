"""
test_vision.py — GPT Vision 와인 라벨 인식 검증 스크립트

사용법:
    cd src
    python test_vision.py                          # 샘플 URL로 테스트
    python test_vision.py /path/to/wine_label.jpg  # 로컬 이미지 파일로 테스트

필요 환경변수 (루트 .env):
    OPENAI_API_KEY=sk-...
"""

import base64
import json
import sys
import os
from pathlib import Path

# 루트 .env 로드
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

try:
    from openai import OpenAI
except ImportError:
    print("openai 패키지가 없습니다. pip install openai 실행 후 재시도하세요.")
    sys.exit(1)


# ────────────────────────────────────────────────────────────
# 프롬프트 (Vue.js composable과 동일)
# ────────────────────────────────────────────────────────────
VISION_PROMPT = """\
이 와인 라벨 이미지를 분석해서 정확히 아래 JSON 형식으로만 반환해주세요.
라벨에서 읽을 수 없거나 불분명한 정보는 null로 처리하세요.

{
  "name": "와인 전체 이름 (예: Château Margaux 2018)",
  "grape_variety": "주요 포도 품종 한국어 또는 원어 (예: Cabernet Sauvignon / 카베르네 소비뇽)",
  "region": "원산지/지역 (예: Bordeaux, France / 보르도, 프랑스)",
  "vintage": 빈티지 연도 숫자 또는 null,
  "wine_type": "red 또는 white 또는 sparkling 또는 rose 중 하나",
  "estimated_tannin": 타닌 강도 0.0~5.0 추정값,
  "estimated_acidity": 산미 강도 0.0~5.0 추정값,
  "estimated_body": 바디감 0.0~5.0 추정값,
  "estimated_sweetness": 당도 0.0~5.0 추정값,
  "confidence": 라벨 인식 신뢰도 0.0~1.0
}

추정 기준:
- 레드 와인: 타닌 높음(3~5), 바디감 보통~높음(2.5~5)
- 화이트 와인: 타닌 낮음(0~1.5), 산미 높음(3~5)
- 스파클링: 산미 높음(3.5~5), 당도 낮음~중간(1~3)
- 로제: 타닌 낮음(1~2.5), 당도 중간(2~3.5)"""


def encode_image_to_base64(image_path: str) -> tuple[str, str]:
    """로컬 이미지를 base64 인코딩 및 MIME 타입 반환"""
    ext = Path(image_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_map.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")
    return b64_data, mime_type


def analyze_wine_label_from_file(image_path: str) -> dict:
    """로컬 이미지 파일로 GPT Vision 분석"""
    b64_data, mime_type = encode_image_to_base64(image_path)
    image_url = f"data:{mime_type};base64,{b64_data}"
    return _call_vision_api(image_url)


def analyze_wine_label_from_url(image_url: str) -> dict:
    """URL 이미지로 GPT Vision 분석 (테스트용)"""
    return _call_vision_api(image_url)


def _call_vision_api(image_url: str) -> dict:
    """OpenAI Vision API 실제 호출"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. 루트 .env를 확인하세요.")

    client = OpenAI(api_key=api_key)

    print("GPT Vision API 호출 중... (gpt-4o-mini)")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "high",  # 고해상도 분석 (라벨 텍스트 정확도 향상)
                        },
                    },
                    {"type": "text", "text": VISION_PROMPT},
                ],
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=500,
        temperature=0.1,  # 일관성 있는 추출 결과
    )

    raw_content = response.choices[0].message.content
    result = json.loads(raw_content)

    # 사용량 출력
    usage = response.usage
    print(f"토큰 사용: 입력 {usage.prompt_tokens} / 출력 {usage.completion_tokens}")

    return result


def format_result(result: dict) -> str:
    """분석 결과를 보기 좋게 출력"""
    lines = [
        "",
        "=" * 50,
        "       GPT Vision 와인 라벨 분석 결과",
        "=" * 50,
        f"  와인 이름  : {result.get('name', '인식 실패')}",
        f"  포도 품종  : {result.get('grape_variety', '-')}",
        f"  원산지     : {result.get('region', '-')}",
        f"  빈티지     : {result.get('vintage', '-')}",
        f"  와인 종류  : {result.get('wine_type', '-')}",
        "",
        "  [맛 프로파일 추정 (0~5)]",
        f"  타닌       : {result.get('estimated_tannin', '-')}",
        f"  산미       : {result.get('estimated_acidity', '-')}",
        f"  바디감     : {result.get('estimated_body', '-')}",
        f"  당도       : {result.get('estimated_sweetness', '-')}",
        "",
        f"  인식 신뢰도: {result.get('confidence', '-')}",
        "=" * 50,
    ]
    return "\n".join(lines)


# ────────────────────────────────────────────────────────────
# 메인 실행
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # 인자로 로컬 파일 경로 전달
        target = sys.argv[1]
        if not os.path.exists(target):
            print(f"파일을 찾을 수 없습니다: {target}")
            sys.exit(1)
        print(f"로컬 이미지 분석 중: {target}")
        result = analyze_wine_label_from_file(target)
    else:
        # 기본 테스트: 공개 와인 라벨 샘플 이미지 URL 사용
        # → 실제 테스트 시 본인이 가진 와인 라벨 이미지 경로를 인자로 넘기세요
        SAMPLE_URL = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/"
            "Biale_Zinfandel_2013.jpg/220px-Biale_Zinfandel_2013.jpg"
        )
        print(f"샘플 이미지 URL로 테스트 중: {SAMPLE_URL}")
        result = analyze_wine_label_from_url(SAMPLE_URL)

    print(format_result(result))
    print("\n[원본 JSON]")
    print(json.dumps(result, ensure_ascii=False, indent=2))
