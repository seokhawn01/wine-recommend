# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**WinePair** — 콜키지 식당 방문 시 AI 소믈리에가 와인 × 메뉴 페어링을 추천해주는 서비스.

### 현재 구현 상태

| 레이어 | 상태 |
|--------|------|
| Python LangChain RAG 파이프라인 (`src/`) | ✅ 완료, 실행 가능 |
| DB: PostgreSQL (Supabase) | ✅ 마이그레이션 완료 (MySQL → PostgreSQL) |
| Vue.js 웹앱 (`frontend/`) | ✅ 8개 페이지 + Supabase Auth 실제 연동 완료 |
| LangGraph 그래프 (`src/graph/`) | ⏳ 다음 구현 단계 — **본인(프론트) 담당** |
| Spring Boot REST API | 📋 설계 완료 — 백엔드 팀원 담당 |
| Python FastAPI + EXAONE 파인튜닝 | 📋 설계 완료 — AI 팀원 담당 |

### 팀 구성 (4명)

| 담당 | 역할 |
|------|------|
| 디자이너 | Figma UI/UX |
| 백엔드 | Spring Boot 3 REST API |
| **프론트 (본인)** | **Vue.js + LangGraph Graph A/B/C + Spring Boot 보조** |
| AI | Python FastAPI + EXAONE 파인튜닝 + Ollama 서빙 |

---

## 실행 방법

**Python 3.12 설치 위치:** `C:\Users\sh088\AppData\Local\Programs\Python\Python312\python.exe`

Git Bash `~/.bashrc`에 별칭 설정:
```bash
alias python='/c/Users/sh088/AppData/Local/Programs\Python\Python312/python.exe'
```

### Python RAG 파이프라인 (`src/`)

```bash
# 1. 패키지 설치 (Python 3.12 필수)
python -m pip install -r requirements.txt

# 2. 환경 변수 설정 (루트 .env — Python 전용)
cp .env.example .env  # DATABASE_URL, OPENAI_API_KEY 필수 입력

# 3. Supabase SQL Editor에서 src/db/schema.sql 실행

# 4. 샘플 데이터 적재
cd src/db && python seed_data.py

# 5. 파이프라인 전체 실행 (ChromaDB 생성)
cd src && python main.py

# 테스트 (반드시 src/ 안에서, main.py로 chroma_db/ 생성 후)
cd src && python test_query.py           # Dense vs Ensemble 비교
cd src && python test_personalized.py   # 개인화 통합 테스트 (5개 시나리오)
```

### Vue.js 프론트엔드 (`frontend/`)

```bash
cd frontend

npm run dev      # 개발 서버 → http://localhost:5173 (포트 충돌 시 5174)
npm run build    # 프로덕션 빌드 → dist/
npm run preview  # 빌드 결과 로컬 미리보기
npm run lint     # oxlint + eslint 순서로 실행 (--fix 포함)
```

---

## 환경 변수

### 루트 `.env` — Python 파이프라인 전용

```
OPENAI_API_KEY=
DATABASE_URL=postgresql+psycopg://postgres:[password]@[host]:5432/postgres
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=wine-recommend
# LLM_BACKEND=ollama   ← EXAONE 사용 시
# LLM_BACKEND=openai   ← GPT fallback (기본값)
```

### `frontend/.env` — Vue.js / Vite 전용 (**루트 `.env`와 별개**)

```
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

> **중요**: Vite는 자신의 프로젝트 루트(`frontend/`)에서만 `.env`를 읽음.
> 루트 `.env`의 `VITE_` 변수는 프론트에 **적용되지 않음**.
> 키 이름은 반드시 `VITE_SUPABASE_ANON_KEY` (PUBLISHABLE_KEY 아님).

---

## 코드 아키텍처

### Python RAG 파이프라인 (`src/`)

#### sys.path 패턴 (중요)

패키지 설치 없이 `sys.path.insert`로 모듈을 참조.

- **`main.py`, 테스트 파일**: `pipeline/`, `db/`, `user/` 경로를 직접 추가 후 flat import
- **각 step 파일 단독 실행**: `__main__` 블록에서 상대 경로로 추가
- **cross-module import**: `try/except ImportError`로 두 가지 경로 모두 처리

#### 8단계 파이프라인

`src/main.py` → `build_pipeline()` → 아래 8단계 순서대로 호출:

| 파일 | 역할 |
|------|------|
| `step1_loader.py` | PostgreSQL 3개 테이블 → LangChain `Document` |
| `step2_splitter.py` | type별 청크 분할 (wine=400, menu=300, restaurant=250자) |
| `step3_embedder.py` | `text-embedding-3-small` 임베딩 모델 |
| `step4_vectorstore.py` | ChromaDB 저장 (`./chroma_db/`, 컬렉션명 `wine_pairing`) |
| `step5_retriever.py` | Dense(60%) + BM25 Sparse(40%) 앙상블 리트리버 |
| `step6_prompt.py` | 소믈리에 프롬프트 + `build_user_context()` |
| `step7_llm.py` | `gpt-4o-mini`, temperature=0.3 |
| `step8_chain.py` | `build_chain()` + `build_personalized_chain()` |

> `step1_loader.py`의 함수명이 `load_documents_from_mysql()`이지만 실제로는 PostgreSQL 연결. 함수명 미변경 상태.

#### 두 가지 Chain

- **`build_chain(retriever, prompt, llm)`**: 기본 체인. `user_context=""`로 비로그인 처리
- **`build_personalized_chain(retriever, user_id, situation, ...)`**: 프로파일 조회 + 식이 제한 필터 + user_context 자동 주입. `RunnableLambda` 클로저 방식

#### 취향 개인화 모듈 (`src/user/`)

**`profile_manager.py`**
- `TasteProfile` 데이터클래스: 탄닌/산미/바디/당도 (0~5) + 선호 향 + 식이 제한
- `update_profile()`: delta 적용 + `_clamp(0.0~5.0)` + `taste_profile_history` 스냅샷
- `filter_menus_by_restrictions(docs, restrictions)`: `RESTRICTION_KEYWORDS` 확장 맵으로 메뉴 Document 필터링

**`feedback_processor.py`**
- `TasteAdjustment`: GPT-4o-mini Structured Output 스키마 (Pydantic BaseModel)
- `save_feedback()`: feedbacks INSERT → GPT 분석 (confidence ≥ 0.5이면 delta × confidence 적용, 미만이면 reaction ±0.1 fallback) → applied=True
- `@traceable` 데코레이터로 LangSmith 추적

#### DB 연결 (`src/db/connection.py`)

`DATABASE_URL` 환경변수 우선. 없으면 `DB_HOST/PORT/USER/PASSWORD/NAME` 개별 변수 조합.
드라이버: `psycopg` (psycopg3). SQLAlchemy 2.0 스타일 (`engine.begin()`, `text()`).

> `test_personalized.py`에 `ON DUPLICATE KEY UPDATE` (MySQL 문법) 잔재 존재. PostgreSQL에서 실행 시 오류 — `ON CONFLICT DO UPDATE`로 수정 필요.

---

### Vue.js 프론트엔드 (`frontend/`)

#### 전체 구조

```
frontend/src/
├── main.js              # Pinia → authStore.init() → app.mount() 순서
├── App.vue              # Navbar 조건부 렌더링 (인증/온보딩 페이지에서 숨김)
├── router/index.js      # 8개 라우트 (가드 없음 — 현재 클라이언트 리디렉션)
├── stores/
│   ├── auth.js          # Supabase Auth 연동 (signInWithPassword/signUp/signOut + 세션 복원)
│   └── taste.js         # 탄닌/산미/바디/당도(0~5), 선호향, 식이제한. getRadarData() → Chart.js
├── lib/
│   └── supabaseClient.js  # createClient(VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY)
├── mock/data.js         # 전체 Mock 데이터 — API 미연동 시 모든 페이지가 이 파일 사용
├── pages/
│   ├── auth/            # LoginPage, SignupPage
│   ├── HomePage         # 식당 목록, 검색/필터
│   ├── RestaurantDetailPage  # 와인 선택 + 메뉴 페어링 ★
│   ├── AiMatchPage      # /match?restaurantId=&wineId=&situation= 쿼리 파라미터 수신
│   ├── OnboardingPage   # 2스텝: 슬라이더 → 향/식이제한
│   ├── MyPage           # 취향 레이더 차트 + 와인 컬렉션
│   └── WineRegisterPage # OCR 탭 / 수동 입력 탭
└── components/
    ├── ui/              # shadcn-vue 수동 구현 (radix-vue + cva + clsx + tailwind-merge)
    └── (비즈니스 컴포넌트)
```

#### Supabase Auth 흐름

```
main.js
  → createPinia() → app.use(pinia)
  → authStore.init()          # getSession() + onAuthStateChange() 등록
  → app.mount('#app')         # 세션 복원 완료 후 마운트

auth.js mapUser()
  supabaseUser.user_metadata.nickname        → user.nickname
  supabaseUser.user_metadata.onboarding_done → user.onboardingDone
```

#### UI 컴포넌트 주의사항

- **shadcn-vue CLI 미사용** — TailwindCSS v4와 호환 안 됨. 모든 컴포넌트 직접 구현
- **`Tabs`**: `provide/inject` 방식. 반드시 `<Tabs>` 안에 `<TabsTrigger>`, `<TabsContent>` 위치해야 함
- **`tailwind.config.js` 없음** — `src/assets/index.css`에 `@import "tailwindcss"` + CSS 변수 정의
- 커스텀 색상: `text-[#722F37]`, `bg-[#FFF8F0]` 형태로 직접 입력 (토큰: 버건디 `#722F37`, 크림 `#FFF8F0`, 골드 `#C5A028`)

#### 현재 Mock 상태

`src/mock/data.js`가 유일한 데이터 소스. `auth.js`만 Supabase 실제 연동됨.
Spring Boot API 연동 시 각 페이지/스토어의 Mock import를 API 호출로 교체.

---

## DB 스키마 (PostgreSQL / Supabase — 7개 테이블)

```
restaurants: restaurant_id(SERIAL), name, food_category, address, corkage_fee, corkage_limit,
             reservation_required, naver_rating, rating(베이지안), feedback_count
menus:       menu_id(SERIAL), restaurant_id, name, category, price, description,
             fattiness(지방성), umami(감칠맛), spiciness(매운맛), sweetness, acidity,
             embedding vector(1536)
wines:       wine_id(SERIAL), name, grape_variety, region, vintage, wine_type,
             tannin, acidity, body, sweetness, aroma, description
users:       user_id(SERIAL), email, password_hash, nickname, onboarding_done
taste_profiles:        profile_id, user_id(UNIQUE), pref_tannin/acidity/body/sweetness,
                       preferred_aromas(JSONB), dietary_restrictions(JSONB),
                       embedding vector(1536)
taste_profile_history: history_id, user_id, feedback_id, pref_*(스냅샷), change_reason
feedbacks:   feedback_id(SERIAL), user_id, wine_id, menu_id, restaurant_id, situation,
             reaction(SMALLINT, 1/-1/0), review_text, profile_adjustments(JSONB), applied
```

> JSONB 컬럼 삽입 시 반드시 `json.dumps(..., ensure_ascii=False)` 후 문자열로 전달 (SQLAlchemy 2.0)

---

## 패키지 버전 (호환 고정)

`requirements.txt`에 `==` 버전 고정. `>=`로 변경 시 pydantic v1/v2 충돌 발생 가능.
- `sqlalchemy==2.0.35` 필수 (2.0.36은 langchain-community 0.3.7과 충돌)
- `psycopg[binary]>=3.1.0` — psycopg3 드라이버
- Python 3.12 필수. 3.14는 `chromadb`, `langchain` 미지원.
- npm 캐시 위치: `D:/npm-cache` (C드라이브 용량 부족으로 변경됨)

---

## 다음 구현 단계 (본인 담당)

### 1순위: LangGraph (`src/graph/`) — 즉시 착수 가능

```bash
pip install langgraph langgraph-checkpoint-postgres
```

구현 순서:
1. `src/graph/state.py` — TypedDict 공유 상태 정의
2. `src/graph/sommelier_graph.py` — Graph A (검색→평가→쿼리확장→생성)
3. `src/graph/feedback_graph.py` — Graph B (기존 `save_feedback()` 노드 분리)
4. LangGraph PostgreSQL 체크포인트 설정 (`langgraph-checkpoint-postgres`)
5. `src/graph/onboarding_graph.py` — Graph C (Human-in-the-loop)

자세한 그래프 설계: `ROADMAP.md` 섹션 7 참조.

### 2순위: Spring Boot API 연동

백엔드 팀원 API 완료 후 `frontend/src/mock/data.js` import를 순서대로 실제 호출로 교체.
