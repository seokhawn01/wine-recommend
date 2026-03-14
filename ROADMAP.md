# WinePair 기술 아키텍처 & 개발 로드맵

---

## 1. 기술 스택

> **아키텍처 결정 (2026-03-08)**: API First 구조.
> AI 기능은 Python FastAPI 서버가 전담. DB는 Supabase PostgreSQL 단일 DB로 통일.

```
     [웹 브라우저] Vue.js
                 │          
      └──────────┬────────────┘
                 ▼
          Spring Boot API        ← 공통 REST API
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
 Supabase              Python FastAPI
 (PostgreSQL           (LangChain + LangGraph)
  + pgvector)
```                     |

### 웹 프론트엔드


| 분류    | 기술                               |
| ----- | -------------------------------- |
| 프레임워크 | Vue.js 3, JavaScript |
| 스타일링  | TailwindCSS v4, shadcn-vue       |
| 차트    | vue-chartjs (취향 레이더 차트)          |
| 폼/검증  | VeeValidate + Zod                |
| 지도    | 네이버 Maps JavaScript API          |
| 배포    | Vercel                           |


### 백엔드 REST API


| 분류     | 기술                      |
| ------ | ----------------------- |
| 프레임워크  | Spring Boot 3 + Kotlin  |
| 인증     | Supabase Auth JWT 검증    |
| 외부 API | 네이버 Local Search API    |
| 배포     | Railway / GCP Cloud Run |


### AI 서버


| 분류       | 기술                                                       |
| -------- | -------------------------------------------------------- |
| 프레임워크    | Python FastAPI                                           |
| AI 파이프라인 | LangChain + LangGraph                                    |
| LLM      | OpenAI API (gpt-4o, gpt-4o-mini, text-embedding-3-small) |
| OCR 파싱   | GPT-4o-mini Vision (이미지 직접 분석, Google Vision API 불필요)   |
| 벡터스토어    | ChromaDB (RAG 검색), pgvector (페어링 점수 계산)                  |
| 배포       | Railway / GCP Cloud Run                                  |


### 공통 인프라


| 분류        | 기술                                                |
| --------- | ------------------------------------------------- |
| DB / 스토리지 | Supabase (PostgreSQL + pgvector + Storage + Auth) |


---

## 2. 데이터 모델 (PostgreSQL / Supabase — 단일 DB)

> PostgreSQL (Supabase) 단일 DB 통일 **완료**.
> Python 파이프라인, Spring Boot API, 웹/앱 모두 동일한 Supabase PostgreSQL 사용.
> 마이그레이션 완료 파일: `src/db/schema.sql`, `src/db/connection.py`, `src/db/seed_data.py`

### users


| 필드                   | 설명                | 타입        |
| -------------------- | ----------------- | --------- |
| id                   | Supabase Auth UID | UUID      |
| email                | 이메일               | TEXT      |
| onboarding_completed | 온보딩 완료 여부         | BOOLEAN   |
| created_at           | 가입일시              | TIMESTAMP |


### taste_profiles


| 필드                   | 설명              | 타입           |
| -------------------- | --------------- | ------------ |
| id                   | 고유 식별자          | UUID         |
| user_id              | → users.id      | UUID         |
| sweetness            | 당도 (0.0~5.0)    | FLOAT        |
| acidity              | 산미 (0.0~5.0)    | FLOAT        |
| body                 | 바디감 (0.0~5.0)   | FLOAT        |
| tannin               | 탄닌 (0.0~5.0)    | FLOAT        |
| preferred_aromas     | 선호 향 배열         | TEXT[]       |
| dietary_restrictions | 못먹는 음식 배열       | TEXT[]       |
| embedding            | 취향 임베딩 벡터       | vector(1536) |
| recorded_at          | 기록 시점 (시계열 추적용) | TIMESTAMP    |


> 취향 슬라이더 값 = 일반 와인 선호도 (와인 미선택 시 페어링 점수 계산에 폴백)

### restaurants


| 필드              | 설명                 | 타입      |
| --------------- | ------------------ | ------- |
| id              | 고유 식별자             | UUID    |
| name            | 식당명                | TEXT    |
| address         | 주소                 | TEXT    |
| latitude        | 위도                 | FLOAT   |
| longitude       | 경도                 | FLOAT   |
| phone           | 전화번호               | TEXT    |
| category        | 음식 카테고리            | TEXT    |
| corkage_fee     | 콜키지 비용 (원, 0이면 무료) | INTEGER |
| corkage_limit   | 병 수 제한             | INTEGER |
| corkage_notes   | 콜키지 조건 비고          | TEXT    |
| operating_hours | 영업시간               | JSONB   |
| naver_place_id  | 네이버 장소 ID          | TEXT    |
| rating          | 앱 내 자체 별점          | FLOAT   |


### menus


| 필드            | 설명                     | 타입           |
| ------------- | ---------------------- | ------------ |
| id            | 고유 식별자                 | UUID         |
| restaurant_id | → restaurants.id       | UUID         |
| name          | 메뉴명                    | TEXT         |
| price         | 가격 (원)                 | INTEGER      |
| category      | 메뉴 카테고리 (전채/메인/디저트/음료) | TEXT         |
| fattiness     | 지방성 (0.0~5.0)          | FLOAT        |
| umami         | 감칠맛                    | FLOAT        |
| sweetness     | 단맛                     | FLOAT        |
| spiciness     | 매운맛                    | FLOAT        |
| saltiness     | 짠맛                     | FLOAT        |
| sourness      | 신맛                     | FLOAT        |
| embedding     | 메뉴 텍스트 임베딩             | vector(1536) |
| created_at    | 등록일시                   | TIMESTAMP    |


> 초기 메뉴 데이터는 운영자가 Supabase에 직접 수기 입력 (별도 admin 도구 없음)

### wines


| 필드              | 설명            | 타입        |
| --------------- | ------------- | --------- |
| id              | 고유 식별자        | UUID      |
| user_id         | → users.id    | UUID      |
| name            | 와인명           | TEXT      |
| grape_variety   | 품종            | TEXT      |
| vintage         | 빈티지 연도        | INTEGER   |
| region          | 지역            | TEXT      |
| label_image_url | 라벨 이미지 URL    | TEXT      |
| tannin          | 탄닌 (0.0~5.0)  | FLOAT     |
| acidity         | 산미 (0.0~5.0)  | FLOAT     |
| body            | 바디감 (0.0~5.0) | FLOAT     |
| sweetness       | 당도 (0.0~5.0)  | FLOAT     |
| created_at      | 등록일시          | TIMESTAMP |


### feedbacks


| 필드                  | 설명                       | 타입        |
| ------------------- | ------------------------ | --------- |
| id                  | 고유 식별자                   | UUID      |
| user_id             | → users.id               | UUID      |
| restaurant_id       | → restaurants.id         | UUID      |
| menu_id             | → menus.id               | UUID      |
| wine_id             | → wines.id (선택, NULL 가능) | UUID      |
| situation           | 오늘의 상황                   | TEXT      |
| rating              | 평가 (good / bad)          | TEXT      |
| review_text         | 자유 텍스트 후기 (선택)           | TEXT      |
| profile_adjustments | GPT가 추출한 취향 조정값 로그       | JSONB     |
| taste_snapshot      | 피드백 시점 취향 스냅샷            | JSONB     |
| created_at          | 피드백 일시                   | TIMESTAMP |


---

## 3. 핵심 파이프라인 상세

### 3.1 와인 라벨 OCR 등록 파이프라인 (F-16)

```
라벨 사진 촬영 (MediaDevices API, capture="environment") 또는 갤러리 업로드
    ↓
FileReader API → DataURL(base64) 변환
    ↓
GPT-4o-mini Vision API 호출 (detail: 'high', temperature=0.1, response_format: json_object)
  구현 위치: frontend/src/composables/useWineVision.js
    ↓
구조화 JSON 반환:
  name / grape_variety / region / vintage / wine_type
  tannin / acidity / body / sweetness / confidence
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ ⚠️  [현재 상태 — wines DB 미구축]                                  │
│  tannin / acidity / body / sweetness = GPT 학습 데이터 기반 추정값  │
│  · 유명 와인(Tignanello 등): 훈련 지식 풍부 → 비교적 정확            │
│  · 무명/소규모 생산자 와인: 품종 특성으로 추정 → 부정확 가능            │
│  · 실시간 인터넷 검색 없음 (GPT 훈련 시점 지식만 활용)                │
│                                                                  │
│  [향후 개선 — wines DB 구축 후]                                    │
│  wines 테이블에서 이름 매칭 검색 →                                   │
│    매칭 성공: DB의 검증된 수치 사용                                   │
│    매칭 실패: GPT 추정값 폴백 (현재 동작)                            │
└─────────────────────────────────────────────────────────────────┘
    ↓
confidence < 0.6 → 경고 표시 + 수동 수정 유도
confidence ≥ 0.6 → 폼 자동 채우기
    ↓
사용자 슬라이더로 최종 수동 수정 가능
    ↓
wines 테이블 저장 (Supabase) ← Spring Boot API 연동 전까지 미구현
```

### 3.2 메뉴 페어링 점수 계산 (식당 상세 진입 시, F-12)

```

[와인 선택 시] wines 테이블에서 선택 와인 특성값 조회
[미선택 시]   taste_profiles에서 사용자 취향 프로파일 조회 (폴백)
    ↓
못먹는 음식(dietary_restrictions) 해당 메뉴 제외
    ↓
와인 특성값 → 자연어 텍스트 변환
    (예: "탄닌 4.0, 산미 3.5의 풀바디 레드 와인")
    ↓
OpenAI text-embedding-3-small → 쿼리 벡터 생성 (1536차원)
    ↓
pgvector cosine_similarity 검색 → 해당 식당 메뉴 유사도 계산
    ↓
와인-음식 페어링 가중치 적용
    - 탄닌 × 지방성: +2.0  (탄닌이 지방과 결합하여 부드러운 미감)
    - 산미 × 지방성: +1.5  (산미가 기름기를 정리하여 개운함)
    - 탄닌 × 매운맛: -2.5  (둘 다 자극적이어서 충돌)
    - 당도 (와인 >= 음식): +1.0  (와인이 더 달아야 균형)
    - 바디감 × 감칠맛: +1.0  (풍부한 바디가 감칠맛과 조화)
    ↓
메뉴별 최종 페어링 점수 → 식당 상세 메뉴 목록에 ★ 아이콘으로 표시

```

### 3.3 AI 소믈리에 설명 생성 (메뉴 선택 후, F-13)

```

GPT-4o 입력값:
    - 선택 와인 정보 (품종/지역/탄닌/산미/바디감/당도)
    - 오늘의 상황 (데이트/친구모임/비즈니스/혼술/가족모임)
    - 선택 메뉴 맛 프로파일 (fattiness/umami/spiciness 등)
    - 페어링 점수 근거
    ↓
GPT-4o
    → 상황 맞춤 소믈리에 스타일 페어링 이유 2~3문장 생성
    예: "데이트 자리에 딱 어울리는 선택이에요.
        이 와인의 섬세한 탄닌이 스테이크 지방과 만나 ..."
    ↓
AI 매칭 페이지 렌더링
    ↓

피드백 제출 (좋아요/별로 + 텍스트 후기 선택 입력)
    ↓
[텍스트 후기 있을 경우]
GPT-4o-mini → 텍스트에서 선호/비선호 요소 추출
    예: "와인이 너무 강했어요" → 탄닌 과다로 해석
    예: "산미가 음식의 기름기를 잡아줘서 좋았어요" → 산미×지방성 조합 선호 강화
    → Structured Output: { tannin: -0.3, acidity: +0.2, body: 0, sweetness: 0 }
    ↓
confidence ≥ 0.5 → delta × confidence 가중 적용
confidence < 0.5 → 텍스트 없음 분기로 이동
    ↓
[텍스트 없을 경우]
    단순 ±0.1 방향 업데이트 (좋아요=+, 별로=-)
    ↓
taste_profiles 수치 조정 (탄닌/산미/바디감/당도, 0.0~5.0 클램핑)
feedbacks.profile_adjustments 에 조정값 로그 저장
    ↓
다음 추천부터 조정된 프로파일 반영

```

### 3.5 사용자 피드백 기반 식당 별점 업데이트

```

피드백 제출 (좋아요 또는 별로)
    ↓
restaurants 테이블에서 해당 식당의 naver_rating, feedback_count 조회
    ↓
베이지안 가중 평균 공식으로 새 rating 계산:

```
rating = (naver_rating × W + Σ feedback_score) / (W + feedback_count)

- W (초기 가중치) = 10  ← 피드백 10개 분량의 신뢰도를 네이버 별점에 부여
- feedback_score: 좋아요 = 5점, 별로 = 1점
- feedback_count: 해당 식당의 누적 피드백 수

예시:
  네이버 별점 4.0, 피드백 없음 → rating = 4.0
  피드백 5개 (좋아요 4, 별로 1) → (4.0×10 + 4×5 + 1×1) / (10+5) ≈ 4.07
  피드백 50개 (좋아요 40, 별로 10) → (4.0×10 + 40×5 + 10×1) / (10+50) ≈ 4.17
↓
```

restaurants.rating, restaurants.feedback_count 업데이트

```

> 초기 피드백이 적을 때 별점이 과도하게 흔들리는 것을 방지하기 위해 베이지안 방식 사용.
> naver_rating은 운영자 수기 입력 시 한 번만 설정되며 이후 변경되지 않음.

---

## 4. AI 모델 전략 (경진대회 특화)

> **핵심 차별점**: "GPT API를 가져다 쓴 팀" 대신 "와인 도메인에 특화된 AI를 직접 만든 팀"으로 포지셔닝.
> 경진대회 발표 인원 10명 내외 기준, API 비용은 월 $1 미만으로 비용 자체는 문제 없음.
> 파인튜닝의 목적은 **비용 절감이 아닌 기술 차별화**임.

### 채택 모델: EXAONE 3.5 (LG AI Research)


| 항목      | 내용                                                         |
| ------- | ---------------------------------------------------------- |
| 모델      | EXAONE-3.5-7.8B-Instruct                                   |
| 개발사     | LG AI Research                                             |
| 선택 이유   | 한국어 + 영어 이중언어 특화 → 소믈리에 한국어 문장 품질이 Llama3 대비 월등            | |
| 학습 환경   | Google Colab T4 GPU (무료 티어), 예상 학습 시간 1~2시간                |
| 총 비용    | **$0** (Colab 무료 + 로컬 서빙)                                  |


### 2트랙 전략 (발표 당일 안정성 확보)

```

트랙 A — 파인튜닝 모델 (목표):
  EXAONE-3.5 파인튜닝 → Ollama (로컬) → Python FastAPI
  발표 성공 시 "자체 AI" 스토리 완성

트랙 B — GPT Fallback (안전망):
  GPT-4o-mini API → Python FastAPI
  발표 당일 트랙 A 장애 시 환경변수 하나로 즉시 전환

전환 방법 (코드 변경 없음):
  .env: LLM_BACKEND=ollama  ←→  LLM_BACKEND=openai

```

### Knowledge Distillation 파이프라인

GPT(선생 모델)가 생성한 고품질 답변으로 소형 모델(학생 모델)을 훈련하는 기법.

```

  Python FastAPI: OpenAI API와 동일 인터페이스로 추상화

```

### 단계별 우선순위


| 우선순위   | 항목                           | 발표 영향                  |
| ------ | ---------------------------- | ---------------------- |
| 🔴 필수  | Python FastAPI 서버 구축         | Spring Boot ↔ AI 연동 핵심 |
| 🔴 필수  | LangGraph Graph A (소믈리에 추천)  | 핵심 기능 시연               |
| 🟠 권장  | Knowledge Distillation 파이프라인 | 기술 차별화                 |
| 🟠 권장  | EXAONE 파인튜닝 + Ollama 서빙      | 발표 임팩트 최대화             |
| 🟡 보너스 | LangGraph Graph B, C         | 시간 여유 시                |


> 파인튜닝이 시간 내 완성 불가 시: OpenAI Fine-tuning API 대체 (비용 $0.03, 난이도 ★★☆☆☆)

---

## 5. 팀 구성 및 역할 분담

> 팀원 구성: 디자이너 1명, 백엔드 1명, 프론트 1명(본인), AI 1명 — 총 4명
> **본인 (프론트)**: Vue.js 웹 + **LangGraph Graph A/B/C** + Spring Boot 보조


| 담당           | 주요 역할                                                                |
| ------------ | -------------------------------------------------------------------- |
| **백엔드**      | Spring Boot 3 REST API, Supabase DB 관리, 네이버 API 연동                   |
| **프론트 (본인)** | Vue.js 웹 (7페이지), **LangGraph Graph A/B/C**, Spring Boot 보조 |
| **AI**       | Python FastAPI 서버, EXAONE 파인튜닝                                       |


---

### 5.1 팀원별 개발 순서

#### 백엔드


| 순서  | 작업                                                  | 선행 조건   |
| --- | --------------------------------------------------- | ------- |
| 1   | Supabase 프로젝트 생성                                    | —       |
| 2   | Spring Boot 3 + Kotlin 프로젝트 생성                      | 1 완료    |
| 3   | Supabase Auth JWT 검증 미들웨어 + 인증 흐름 구현                | 1, 2 완료 |
| 4   | `GET/PUT /profile` — 취향 프로파일 조회/수정                  | 3 완료    |
| 5   | `GET/POST/DELETE /wines` — 와인 컬렉션 CRUD              | 3 완료    |
| 6   | `GET /restaurants` — 식당 목록 (GPS 기반 필터/정렬)           | 3 완료    |
| 7   | `GET /restaurants/{id}` — 식당 상세 정보                  | 6 완료    |
| 8   | `POST /feedbacks` — 피드백 저장 (AI 서버 위임 stub 포함)       | 3 완료    |
| 9   | 네이버 Local Search API 연동 (`/restaurants`에 통합)        | 6 완료    |
| 10  | Python FastAPI WebClient 설정 + `/recommend` 엔드포인트 연동 | AI 2 완료 |
| 11  | Supabase Storage 연동 (와인 라벨 이미지 업로드)                 | 1 완료    |
| 12  | ~~Google Cloud Vision API~~ — GPT-4o-mini Vision으로 대체 (프론트 직접 호출, 서버 구현 불필요) | —       |
| 13  | 통합 테스트 + 배포                                         | 전체 완료   |


---

#### 프론트 (본인) — LangGraph + Vue.js

> ⚠️ **두 트랙 병렬 진행**: LangGraph(Python)와 Vue.js(Web)는 의존성이 없으므로 동시에 착수.
> LangGraph는 기존 LangChain 파이프라인이 완료된 상태이므로 **지금 즉시 착수 가능**.

**[트랙 A] LangGraph** — 즉시 착수, 기존 `src/pipeline/` 기반


| 순서  | 작업                                                              | 선행 조건                | 파일 위치                           |
| --- | --------------------------------------------------------------- | -------------------- | ------------------------------- |           |
| A-1 | `sommelier_graph.py` — Graph A (검색→평가→쿼리확장→생성)                  | A-1                  | `src/graph/sommelier_graph.py`  |
| A-2 | `feedback_graph.py` — Graph B (기존 `save_feedback()` 노드 분리 리팩토링) | A-1                  | `src/graph/feedback_graph.py`   |
| A-3 | LangGraph PostgreSQL 체크포인트 설정                                   | Supabase 스키마 완료, A-1 | `src/graph/__init__.py`         |
| A-4 | `onboarding_graph.py` — Graph C (Human-in-the-loop 취향 대화)       | A-1, A-4             | `src/graph/onboarding_graph.py` |
| A-5 | LangGraph 통합 테스트 (LangSmith 트레이싱 span 확인)                       | A-2 ~ A-5            | —                               |

**[트랙 B] Vue.js** — 프로젝트 세팅은 즉시 착수 / 각 페이지는 디자인+API 순서에 따라


| 순서  | 작업                                                                        | 선행 조건                   |
| --- | ------------------------------------------------------------------------- | ----------------------- |
| ✅ B-1 | Vue.js 3 세팅 (JavaScript, TailwindCSS v4, shadcn-vue, 환경변수 `.env`) | —                       |
| ✅ B-2 | Supabase Auth 실제 연동 완료 (`signInWithPassword` / `signUp` / `signOut` + 세션 자동 복원) | B-1                     |
| ✅ B-3 | 온보딩 페이지 (취향 슬라이더 + 실시간 레이더 차트 vue-chartjs) — **Mock 데이터**         | B-2                     |
| ✅ B-4 | 홈 페이지 (지도 플레이스홀더 + 식당 목록 + 필터/정렬) — **Mock 데이터**                   | B-1                     |
| ✅ B-5 | 식당 상세 페이지 (와인/상황 선택 + 메뉴 페어링 점수 ★ 표시) — **Mock 데이터**              | B-4                     |
| ✅ B-6 | AI 매칭 페이지 (소믈리에 설명 + 피드백 제출 → 취향 업데이트) — **Mock 데이터**             | B-5                     |
| ✅ B-7 | 마이페이지 (취향 레이더 차트 + 와인 컬렉션) — **Mock 데이터**                           | B-3                     |
| ✅ B-8 | 와인 등록 페이지 (OCR 탭 + 수동 입력 탭 + 슬라이더) — **GPT Vision 실제 연동 완료** (`useWineVision` composable). ⚠️ tannin 등 수치는 wines DB 미구축으로 GPT 추정값 사용 중 | B-7                     |
| B-9 | Vercel 배포                                                                 | 전체 완료                   |


---

#### AI

> ### ⚡ 핵심: 파인튜닝은 DB 데이터와 무관하게 즉시 착수 가능
>
> **파인튜닝 모델이 학습하는 것은 DB의 특정 레코드가 아니다.**
> 모델은 세 가지를 학습한다: **소믈리에 문체**, **페어링 원칙(탄닌×지방성 등)**, **상황별 어조**.
> 이는 도메인 관련 데이터면 충분하며 DB의 특정 식당/메뉴/와인 데이터와 일치할 필요가 없다.
>
> ```
> [DB에 있는 데이터]                    [훈련 데이터]
> "티본스테이크, fattiness=4.5"   ≠   "안심스테이크, fattiness=4.2"  (이름 달라도 OK)
> "까베르네 소비뇽, tannin=4.0"   ≠   "보르도 레드, tannin=3.8"      (다른 와인도 OK)
>
> 모델은 "높은 탄닌 + 높은 지방성 + 데이트 → 소믈리에 스타일 한국어 설명" 패턴을 학습.
> 추론 시 DB의 실제 값이 들어오면 학습한 패턴을 일반화해서 생성. ✅
> ```
>
> **단 하나의 사전 합의 필요: Prompt Format**
> 훈련 데이터의 입력 형식과 LangGraph `generate_explanation` 노드의 입력 형식이 반드시 동일해야 한다.
> **AI 팀원과 프론트(본인)가 개발 시작 전 prompt template을 먼저 문서화할 것.**
>
> ```
> # 합의된 prompt format 예시
> "[와인] 탄닌={tannin}, 산미={acidity}, 바디감={body}, 당도={sweetness}
>  [음식] 지방성={fattiness}, 감칠맛={umami}, 매운맛={spiciness}
>  [상황] {situation}
>  → 소믈리에 추천:"
> ```


| 순서    | 작업                                                                    | 선행 조건                        |
| ----- | --------------------------------------------------------------------- | ---------------------------- |
| 0     | **프론트(본인)와 prompt format 합의 후 문서화**                                   | ← **가장 먼저**                  |
| 1     | Python FastAPI 서버 기반 구축 (프로젝트 구조, 헬스체크 `/health`)                     |                              |
| **2** | **Knowledge Distillation: 와인 API 데이터 정제 + GPT-4o 학습 데이터 300~500개 생성** | **0 완료 (DB 불필요 — 즉시 착수 가능)** |
| **3** | **EXAONE-3.5 QLoRA 파인튜닝 (Google Colab T4 + Unsloth)**                 | **3 완료 (DB·FastAPI 완료 불필요)** |
| 4     | LangGraph Graph A/B와 FastAPI 엔드포인트 연동                                 | 2 완료, 프론트 A-2·A-3 완료         |
| 5     | FastAPI `LLM_BACKEND` 환경변수 전환 로직 + EXAONE 연동                          | 5, 6 완료                      |


---

### 5.2 전체 의존성 및 착수 가능 시점

```

[Day 1 — 전원 즉시 착수 가능]
  백엔드:       1. Supabase 스키마 실행
  프론트(본인): A-1. LangGraph state.py  +  B-1. Vue.js 세팅
  AI:           0. 프론트와 prompt format 합의
                1. FastAPI 서버 기반 구축
                3. KD 데이터 생성 + 파인튜닝  ← DB 완료 안 기다려도 됨!

[순차 해제되는 블로커]
  백엔드 1 완료 (Supabase 스키마)
    → 백엔드 2 Spring Boot 연결 가능
    → 프론트 A-4 LangGraph 체크포인트 설정 가능
    → AI FastAPI DB 연동 가능

  백엔드 3 완료 (JWT 미들웨어)
    → 프론트 B-2 Auth 연동 시작 가능

  AI 2 완료 (FastAPI /recommend stub)
    → 백엔드 10 WebClient 연동 테스트 가능
    → 프론트 B-6 AI 매칭 페이지 개발 가능

  프론트 A-2·A-3 완료 (Graph A, B)
    → AI 3 FastAPI + LangGraph 연동 착수 가능

---

### 5.3 본인(프론트) 집중도 가이드

두 트랙 + Spring Boot 보조까지 담당하므로 시점별 집중 영역을 구분한다.


| 시기      | 집중 트랙                                      | 이유                                      |
| ------- | ------------------------------------------ | --------------------------------------- |
| **초반**  | **LangGraph A-1 → A-2 → A-3** 우선           | 의존성 없이 즉시 착수 가능, AI 팀 FastAPI 연동 블로커 해소 |
| **중반**  | **Vue.js B-1 → B-2 → B-3 → B-4**           | 디자인 2·3단계와 백엔드 API가 준비되는 시점             |
| **후반**  | **Vue.js B-5 → B-6 + LangGraph A-4 → A-5** | AI 서버 연동 후 통합, Graph C는 마지막             |
| **마무리** | **B-7 → B-8 → B-9 + A-6 통합 테스트**           | 모든 의존성 해소 후 마무리 통합                      |


---

## 6. Python AI 파이프라인 구현 현황

> **현재 상태**: Python LangChain RAG 파이프라인 구현 완료. LangGraph 구체화 진행 중.

```

src/
├── main.py                    # 파이프라인 진입점
├── test_query.py              # 기본 쿼리 테스트 (Dense vs Ensemble 비교)
├── test_personalized.py       # 개인화 통합 테스트 (5개 통과)
├── pipeline/
│   ├── step1_loader.py        # PostgreSQL 3테이블 → LangChain Document
│   ├── step2_splitter.py      # type별 청크 분할 (wine=400, menu=300, restaurant=250)
│   ├── step3_embedder.py      # text-embedding-3-small
│   ├── step4_vectorstore.py   # ChromaDB 저장 (./chroma_db/)
│   ├── step5_retriever.py     # Dense(60%) + Sparse/BM25(40%) 앙상블
│   ├── step6_prompt.py        # 소믈리에 프롬프트 + build_user_context()
│   ├── step7_llm.py           # gpt-4o-mini, temperature=0.3
│   └── step8_chain.py         # build_chain() + build_personalized_chain()
├── db/
│   ├── schema.sql             # PostgreSQL 7개 테이블 정의 (Supabase)
│   ├── connection.py          # SQLAlchemy 엔진/세션
│   └── seed_data.py           # 샘플 데이터 (와인 10, 식당 5, 메뉴 30)
└── user/
    ├── profile_manager.py     # TasteProfile CRUD + 식이 제한 필터링
    └── feedback_processor.py  # GPT Structured Output 취향 학습

```

### 완료된 주요 구현


| 구분                   | 완료 항목                                                                                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **P0 LangChain RAG** | PostgreSQL 3테이블 로드 → 청크 분할 → 임베딩 → ChromaDB → Dense+BM25 앙상블 → 소믈리에 프롬프트 → gpt-4o-mini → LCEL Chain                                              |
| **P1 취향 개인화**        | TasteProfile CRUD + 0~5 클램핑 + 식이 제한 필터 + GPT Structured Output 취향 학습 + confidence 가중 업데이트 + reaction fallback + 이력 스냅샷 + 개인화 체인 + LangSmith 트레이싱 |


---

## 7. 개발 로드맵

### [진행 예정] LangGraph 구체화 (A-1 ~ A-5)

현재 선형 체인(linear chain)을 **상태 기반 그래프(StateGraph)**로 전환하여
조건부 라우팅, 재시도 루프, Human-in-the-loop 지원을 추가한다.

```

src/
└── graph/
    ├── **init**.py
    ├── state.py               # TypedDict 상태 정의 (공유)
    ├── nodes/
    │   ├── retrieval.py       # 검색 + 식이 제한 필터 노드
    │   ├── evaluator.py       # 검색 결과 품질 평가 노드
    │   ├── pairing.py         # 페어링 근거 분석 노드
    │   ├── generation.py      # 소믈리에 설명 생성 노드
    │   └── feedback.py        # 피드백 분석 + 취향 업데이트 노드
    ├── sommelier_graph.py     # Graph A: 소믈리에 추천
    ├── feedback_graph.py      # Graph B: 피드백 처리
    └── onboarding_graph.py    # Graph C: 취향 온보딩 대화

```

#### Graph A: 소믈리에 추천 그래프

현재 `build_personalized_chain()` → `SommelierGraph`로 전환

**SommelierState:**

```

question, user_id, situation
→ user_profile, user_context_text
→ retrieved_docs, filtered_docs, retrieval_attempts
→ retrieval_sufficient, pairing_rationale
→ recommendation

```

**그래프 흐름:**

```

START
  ↓
[load_user_profile]   취향 프로파일 + user_context 텍스트 생성
  ↓
[retrieve_docs]       앙상블 검색 (retrieval_attempts++)
  ↓
[filter_docs]         식이 제한 키워드 기반 메뉴 Document 제거
  ↓
[evaluate_results]    와인 ≥ 1개 AND 메뉴 ≥ 1개 → sufficient 판정
  ├─ sufficient=True  ──────────────────────────────────→ [analyze_pairing]
  ├─ sufficient=False AND attempts < 2  → [expand_query] → [retrieve_docs]
  └─ sufficient=False AND attempts ≥ 2 ────────────────→ [analyze_pairing]
                                                              ↓
                                                     [generate_explanation]
                                                              ↓
                                                            END

```

**핵심 이점:**

- 검색 결과 부족 시 GPT-4o-mini로 쿼리 확장 후 자동 재시도 (최대 2회)
- 와인 전문 용어 보강 → BM25 검색 정확도 향상
- 각 노드 상태가 LangSmith에서 별도 span으로 추적됨

#### Graph B: 피드백 처리 그래프

현재 `save_feedback()` 선형 함수 → FeedbackGraph로 전환

**그래프 흐름:**

```

START
  ↓
[save_feedback_record]    feedbacks INSERT (applied=False)
  ↓
[check_review_text]       len(review) ≥ 5자?
  ├─ Yes → [analyze_with_gpt]      GPT Structured Output 분석
  │           ↓
  │         [check_confidence]     confidence ≥ 0.5?
  │           ├─ Yes → [apply_gpt_delta]      delta × confidence 가중 업데이트
  │           └─ No  → [apply_reaction_delta] ±0.1 소폭 업데이트
  └─ No  → [apply_reaction_delta]
                ↓
         [mark_applied]    feedbacks.applied = True
                ↓
              END

```

#### Graph C: 취향 온보딩 대화 그래프 (신규)

숫자 슬라이더 대신 **자연어 대화**로 취향을 파악하는 에이전트.

**그래프 흐름:**

```

START
  ↓
[welcome]         첫 인사 + 오픈 질문 생성
  ↓
[user_input]      사용자 응답 대기 (Human-in-the-loop)
  ↓
[extract_profile] 대화에서 TasteProfile 수치 추출 (GPT Structured Output)
  ↓
[evaluate_complete] 4개 차원 + 식이제한 충분히 파악됐는지 판단
  ├─ 완료 → [confirm_profile]  "이렇게 이해했어요, 맞나요?" 확인
  │             ├─ 확인 → [save_profile] DB 저장 → END
  │             └─ 수정 → [user_input] 재수집
  └─ 미완 (turn < 5) → [ask_followup] 부족한 차원 추가 질문 → [user_input]
       │
  미완 (turn ≥ 5) → [save_partial_profile] 기본값 채워서 저장 → END

```

**GPT 추출 Structured Output:**

```json
{
  "pref_tannin": 1.5,
  "pref_acidity": 3.0,
  "pref_body": 2.0,
  "pref_sweetness": 2.5,
  "preferred_aromas": ["과일"],
  "dietary_restrictions": ["해산물"],
  "confidence": 0.7,
  "missing_aspects": ["당도 선호도"]
}
```

#### 구현 순서


| 순서  | 그래프              | 우선 이유                   |
| --- | ---------------- | ----------------------- |
| 1   | Graph A: 소믈리에 추천 | 현재 파이프라인과 직접 연결, 임팩트 최대 |
| 2   | Graph B: 피드백 처리  | 기존 코드 리팩토링, 상태 가시성 확보   |
| 3   | Graph C: 온보딩 대화  | 신규 기능, Vue.js 연동 시 필요   |


#### 패키지 설치

```bash
pip install langgraph langgraph-checkpoint-postgres
```

> `langgraph-checkpoint-sqlite` 대신 `langgraph-checkpoint-postgres` 사용.
> Supabase 단일 DB 원칙 유지 — LangGraph 상태도 PostgreSQL에 저장.
>
>

