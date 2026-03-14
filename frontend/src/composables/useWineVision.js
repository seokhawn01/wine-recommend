/**
 * useWineVision.js — GPT Vision으로 와인 라벨 이미지 분석 composable
 *
 * ⚠️ 현재는 테스트 목적으로 프론트에서 직접 OpenAI API를 호출합니다.
 *    프로덕션 배포 시에는 VITE_OPENAI_API_KEY가 브라우저에 노출되므로
 *    Spring Boot API 프록시를 통해 호출하도록 교체해야 합니다.
 *
 * 사용법:
 *   const { analyzeWineLabel, isLoading, error } = useWineVision()
 *   const result = await analyzeWineLabel(imageDataUrl) // FileReader DataURL
 *
 * 환경변수 (frontend/.env):
 *   VITE_OPENAI_API_KEY=sk-...
 */

import { ref } from 'vue'

// ────────────────────────────────────────────────────────────
// 프롬프트 (src/test_vision.py와 동일)
// ────────────────────────────────────────────────────────────
const VISION_PROMPT = `이 와인 라벨 이미지를 분석해서 정확히 아래 JSON 형식으로만 반환해주세요.
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
- 로제: 타닌 낮음(1~2.5), 당도 중간(2~3.5)`

// ────────────────────────────────────────────────────────────
// API 호출
// ────────────────────────────────────────────────────────────
/**
 * OpenAI Vision API 호출
 * @param {string} imageDataUrl - FileReader가 반환한 data:image/...;base64,... 형태
 * @returns {Promise<object>} GPT가 반환한 JSON 파싱 결과
 */
async function callVisionApi(imageDataUrl) {
  const apiKey = import.meta.env.VITE_OPENAI_API_KEY
  if (!apiKey) {
    throw new Error('VITE_OPENAI_API_KEY가 설정되지 않았습니다. frontend/.env를 확인하세요.')
  }

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'image_url',
              image_url: {
                url: imageDataUrl,  // DataURL 그대로 전달 (base64 내장)
                detail: 'high',      // 고해상도: 라벨 텍스트 인식 정확도 향상
              },
            },
            { type: 'text', text: VISION_PROMPT },
          ],
        },
      ],
      response_format: { type: 'json_object' },
      max_tokens: 500,
      temperature: 0.1,
    }),
  })

  if (!response.ok) {
    const errBody = await response.json().catch(() => ({}))
    throw new Error(errBody.error?.message ?? `OpenAI API 오류: ${response.status}`)
  }

  const data = await response.json()
  return JSON.parse(data.choices[0].message.content)
}

// ────────────────────────────────────────────────────────────
// 결과를 form 구조로 변환
// ────────────────────────────────────────────────────────────
/**
 * GPT 응답 → WineRegisterPage / OcrPage form 구조로 변환
 * @param {object} raw - GPT JSON 응답
 * @returns {{ name, grape, region, vintage, type, tannin, acidity, body, sweetness, confidence }}
 */
function mapToForm(raw) {
  const clamp = (val, fallback = 2.5) => {
    const n = parseFloat(val)
    return isNaN(n) ? fallback : Math.min(5, Math.max(0, n))
  }

  const validTypes = ['red', 'white', 'sparkling', 'rose']
  const wineType = validTypes.includes(raw.wine_type) ? raw.wine_type : 'red'

  return {
    name: raw.name ?? '',
    grape: raw.grape_variety ?? '',
    region: raw.region ?? '',
    vintage: raw.vintage ? String(raw.vintage) : '',
    type: wineType,
    tannin: clamp(raw.estimated_tannin),
    acidity: clamp(raw.estimated_acidity),
    body: clamp(raw.estimated_body),
    sweetness: clamp(raw.estimated_sweetness),
    confidence: clamp(raw.confidence, 0),
  }
}

// ────────────────────────────────────────────────────────────
// Composable 본체
// ────────────────────────────────────────────────────────────
export function useWineVision() {
  const isLoading = ref(false)
  const error = ref(/** @type {string|null} */ (null))

  /**
   * 와인 라벨 이미지를 GPT Vision으로 분석
   * @param {string} imageDataUrl - FileReader DataURL (data:image/...;base64,...)
   * @returns {Promise<ReturnType<mapToForm>|null>} 실패 시 null 반환
   */
  async function analyzeWineLabel(imageDataUrl) {
    isLoading.value = true
    error.value = null

    try {
      const raw = await callVisionApi(imageDataUrl)
      return mapToForm(raw)
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
      console.error('[useWineVision] 분석 실패:', e)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return { analyzeWineLabel, isLoading, error }
}
