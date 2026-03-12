-- ============================================================
-- WinePair 데이터베이스 스키마 v2.0
-- Supabase PostgreSQL + pgvector
-- ROADMAP.md 기준 (2026-03-10)
-- Supabase SQL Editor에서 실행
-- ============================================================


-- ============================================================
-- 확장 모듈
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;       -- 벡터 임베딩 (pgvector)


-- ============================================================
-- 1. users — Supabase Auth 연동 프로필
-- ============================================================
-- auth.users(id)를 PK로 참조 → 별도 password 관리 불필요
CREATE TABLE IF NOT EXISTS public.users (
  id                   UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email                TEXT        NOT NULL,
  nickname             TEXT,
  onboarding_completed BOOLEAN     NOT NULL DEFAULT FALSE,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.users IS '사용자 프로필 (Supabase Auth auth.users 확장)';

-- Supabase Auth 신규 가입 시 자동으로 users 행 생성
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, nickname)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'nickname'
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- ============================================================
-- 2. restaurants — 콜키지 식당
-- ============================================================
CREATE TABLE IF NOT EXISTS public.restaurants (
  id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT         NOT NULL,
  address         TEXT,
  latitude        FLOAT,
  longitude       FLOAT,
  phone           TEXT,
  category        TEXT,                           -- 음식 카테고리 (한식/양식/일식 등)
  corkage_fee     INTEGER      NOT NULL DEFAULT 0, -- 콜키지 비용 (원, 0이면 무료)
  corkage_limit   INTEGER,                        -- 병 수 제한 (NULL이면 무제한)
  corkage_notes   TEXT,                           -- 콜키지 조건 비고
  operating_hours JSONB,                          -- 영업시간 {"mon": "11:00-22:00", ...}
  naver_place_id  TEXT,                           -- 네이버 장소 ID
  naver_rating    DECIMAL(3,2) CHECK (naver_rating >= 0.0 AND naver_rating <= 5.0),
  rating          DECIMAL(3,2) CHECK (rating >= 0.0 AND rating <= 5.0), -- 베이지안 가중 평균
  feedback_count  INTEGER      NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN public.restaurants.rating         IS '베이지안 가중 평균: (naver_rating×10 + Σscores) / (10 + feedback_count)';
COMMENT ON COLUMN public.restaurants.naver_rating   IS '운영자 수기 입력, 이후 변경 없음';
COMMENT ON COLUMN public.restaurants.corkage_fee    IS '0이면 무료 콜키지';


-- ============================================================
-- 3. menus — 식당 메뉴
-- ============================================================
CREATE TABLE IF NOT EXISTS public.menus (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  restaurant_id UUID        NOT NULL REFERENCES public.restaurants(id) ON DELETE CASCADE,
  name          TEXT        NOT NULL,
  price         INTEGER,
  category      TEXT,                             -- 전채/메인/디저트/음료
  -- 맛 프로파일 (0.0~5.0)
  fattiness     DECIMAL(3,1) NOT NULL DEFAULT 0.0 CHECK (fattiness  >= 0.0 AND fattiness  <= 5.0),
  umami         DECIMAL(3,1) NOT NULL DEFAULT 0.0 CHECK (umami      >= 0.0 AND umami      <= 5.0),
  sweetness     DECIMAL(3,1) NOT NULL DEFAULT 0.0 CHECK (sweetness  >= 0.0 AND sweetness  <= 5.0),
  spiciness     DECIMAL(3,1) NOT NULL DEFAULT 0.0 CHECK (spiciness  >= 0.0 AND spiciness  <= 5.0),
  saltiness     DECIMAL(3,1) NOT NULL DEFAULT 0.0 CHECK (saltiness  >= 0.0 AND saltiness  <= 5.0),
  sourness      DECIMAL(3,1) NOT NULL DEFAULT 0.0 CHECK (sourness   >= 0.0 AND sourness   <= 5.0),
  embedding     vector(1536),                     -- 메뉴 텍스트 임베딩 (pgvector)
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.menus IS '초기 메뉴 데이터는 운영자가 Supabase에 직접 입력';


-- ============================================================
-- 4. wines — 사용자 개인 와인 컬렉션
-- ============================================================
CREATE TABLE IF NOT EXISTS public.wines (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID        REFERENCES public.users(id) ON DELETE SET NULL, -- NULL이면 시스템 공통 와인
  name            TEXT        NOT NULL,
  grape_variety   TEXT,
  vintage         INTEGER     CHECK (vintage >= 1800 AND vintage <= 2100),
  region          TEXT,
  wine_type       TEXT        CHECK (wine_type IN ('red', 'white', 'rosé', 'sparkling', 'dessert', 'fortified')),
  label_image_url TEXT,                           -- Supabase Storage URL
  -- 와인 특성 (0.0~5.0) — 페어링 점수 계산에 사용
  tannin          DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (tannin    >= 0.0 AND tannin    <= 5.0),
  acidity         DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (acidity   >= 0.0 AND acidity   <= 5.0),
  body            DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (body      >= 0.0 AND body      <= 5.0),
  sweetness       DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (sweetness >= 0.0 AND sweetness <= 5.0),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN public.wines.user_id IS 'NULL이면 시스템 공통 와인 카탈로그';


-- ============================================================
-- 5. taste_profiles — 취향 프로파일 (시계열)
-- ============================================================
-- 취향 변경 시 UPDATE 대신 새 행을 INSERT → 이력 자동 보존
-- 현재 프로파일 조회: latest_taste_profiles 뷰 사용
CREATE TABLE IF NOT EXISTS public.taste_profiles (
  id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  -- 와인 선호도 (0.0~5.0)
  tannin               DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (tannin    >= 0.0 AND tannin    <= 5.0),
  acidity              DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (acidity   >= 0.0 AND acidity   <= 5.0),
  body                 DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (body      >= 0.0 AND body      <= 5.0),
  sweetness            DECIMAL(3,1) NOT NULL DEFAULT 2.5 CHECK (sweetness >= 0.0 AND sweetness <= 5.0),
  preferred_aromas     TEXT[]      NOT NULL DEFAULT '{}',  -- 선호 향 배열 (과일, 오크, 꽃 등)
  dietary_restrictions TEXT[]      NOT NULL DEFAULT '{}',  -- 못 먹는 음식 (해산물, 유제품 등)
  embedding            vector(1536),                       -- 취향 벡터 (pgvector)
  recorded_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- 기록 시점 (시계열 추적용)
);

COMMENT ON TABLE  public.taste_profiles              IS '취향 변경마다 INSERT → 시계열 이력 자동 보존. 현재값은 latest_taste_profiles 뷰 참조';
COMMENT ON COLUMN public.taste_profiles.recorded_at  IS '이 시점의 취향 스냅샷';


-- ============================================================
-- 6. feedbacks — 피드백 및 취향 개인화
-- ============================================================
CREATE TABLE IF NOT EXISTS public.feedbacks (
  id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID        NOT NULL REFERENCES public.users(id)        ON DELETE CASCADE,
  restaurant_id       UUID        NOT NULL REFERENCES public.restaurants(id)  ON DELETE CASCADE,
  menu_id             UUID        NOT NULL REFERENCES public.menus(id)        ON DELETE CASCADE,
  wine_id             UUID        REFERENCES public.wines(id) ON DELETE SET NULL, -- 선택, NULL 가능
  situation           TEXT,                     -- 오늘의 상황 (데이트/친구모임/비즈니스 등)
  rating              TEXT        CHECK (rating IN ('good', 'bad')),
  review_text         TEXT,                     -- 자유 텍스트 후기 (선택)
  profile_adjustments JSONB,                    -- GPT가 추출한 취향 조정값 로그
  taste_snapshot      JSONB,                    -- 피드백 시점 취향 스냅샷 (나중에 비교용)
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN public.feedbacks.profile_adjustments IS 'GPT Structured Output 결과: {tannin: +0.2, acidity: -0.1, ...}';
COMMENT ON COLUMN public.feedbacks.taste_snapshot       IS '피드백 제출 시점 taste_profiles 스냅샷';


-- ============================================================
-- 인덱스
-- ============================================================

-- restaurants: 위치 기반 검색 + 카테고리 필터
CREATE INDEX IF NOT EXISTS idx_restaurants_location      ON public.restaurants (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_restaurants_naver_place_id ON public.restaurants (naver_place_id);
CREATE INDEX IF NOT EXISTS idx_restaurants_category      ON public.restaurants (category);

-- menus: 식당별 조회 (자주 사용)
CREATE INDEX IF NOT EXISTS idx_menus_restaurant_id ON public.menus (restaurant_id);
-- 메뉴 벡터 인덱스 — 데이터 1000건 이상 시 주석 해제 후 실행
-- CREATE INDEX idx_menus_embedding ON public.menus USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- wines: 사용자별 컬렉션 조회
CREATE INDEX IF NOT EXISTS idx_wines_user_id ON public.wines (user_id);

-- taste_profiles: 사용자별 최신 프로파일 조회
CREATE INDEX IF NOT EXISTS idx_taste_profiles_user_recorded ON public.taste_profiles (user_id, recorded_at DESC);

-- feedbacks: 사용자별, 식당별, 최신순
CREATE INDEX IF NOT EXISTS idx_feedbacks_user_id      ON public.feedbacks (user_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_restaurant_id ON public.feedbacks (restaurant_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_created_at   ON public.feedbacks (created_at DESC);


-- ============================================================
-- VIEW: 사용자별 최신 취향 프로파일
-- ============================================================
CREATE OR REPLACE VIEW public.latest_taste_profiles AS
SELECT DISTINCT ON (user_id) *
FROM public.taste_profiles
ORDER BY user_id, recorded_at DESC;

COMMENT ON VIEW public.latest_taste_profiles IS '각 사용자의 가장 최근 취향 프로파일. taste_profiles에서 INSERT로 이력 관리 시 이 뷰로 현재값 조회';


-- ============================================================
-- 함수: 베이지안 식당 별점 업데이트
-- ============================================================
-- 공식: rating = (naver_rating × 10 + Σ scores) / (10 + feedback_count)
-- 점수: good → 5점, bad → 1점
-- 사용: SELECT public.update_restaurant_rating('restaurant-uuid', 'good');
CREATE OR REPLACE FUNCTION public.update_restaurant_rating(
  p_restaurant_id UUID,
  p_rating        TEXT   -- 'good' or 'bad'
)
RETURNS VOID AS $$
DECLARE
  v_rating         DECIMAL(3,2);
  v_feedback_count INTEGER;
  v_score          INTEGER;
  v_new_rating     DECIMAL(3,2);
  v_weight CONSTANT INTEGER := 10;  -- 네이버 별점 초기 가중치
BEGIN
  -- 현재 별점과 피드백 수 조회
  SELECT rating, feedback_count
  INTO v_rating, v_feedback_count
  FROM public.restaurants
  WHERE id = p_restaurant_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION '식당을 찾을 수 없습니다: %', p_restaurant_id;
  END IF;

  v_score := CASE WHEN p_rating = 'good' THEN 5 ELSE 1 END;

  -- 베이지안 점진 업데이트 (기존 rating으로 역산)
  -- new_rating = (rating × (W + count) + new_score) / (W + count + 1)
  v_new_rating := (
    v_rating * (v_weight + v_feedback_count) + v_score
  ) / (v_weight + v_feedback_count + 1);

  UPDATE public.restaurants
  SET
    rating         = ROUND(v_new_rating::NUMERIC, 2),
    feedback_count = feedback_count + 1
  WHERE id = p_restaurant_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.update_restaurant_rating IS
  '피드백 제출 시 베이지안 가중 평균으로 식당 별점 업데이트. feedbacks INSERT 후 호출.';


-- ============================================================
-- RLS (Row Level Security) — 보안 정책
-- ============================================================
ALTER TABLE public.users          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.taste_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wines          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedbacks      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.restaurants    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.menus          ENABLE ROW LEVEL SECURITY;

-- users: 본인 프로필만 조회/수정
CREATE POLICY "users_select_own" ON public.users
  FOR SELECT USING (auth.uid() = id);
CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- taste_profiles: 본인 프로파일만 CRUD
CREATE POLICY "taste_profiles_select_own" ON public.taste_profiles
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "taste_profiles_insert_own" ON public.taste_profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- wines: 본인 와인 + 시스템 공통 와인(user_id IS NULL) 조회
CREATE POLICY "wines_select"      ON public.wines
  FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "wines_insert_own"  ON public.wines
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "wines_update_own"  ON public.wines
  FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "wines_delete_own"  ON public.wines
  FOR DELETE USING (auth.uid() = user_id);

-- feedbacks: 본인 피드백만 CRUD
CREATE POLICY "feedbacks_select_own" ON public.feedbacks
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "feedbacks_insert_own" ON public.feedbacks
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- restaurants: 누구나 조회 가능 (공개 데이터)
CREATE POLICY "restaurants_select_all" ON public.restaurants
  FOR SELECT USING (true);

-- menus: 누구나 조회 가능 (공개 데이터)
CREATE POLICY "menus_select_all" ON public.menus
  FOR SELECT USING (true);
