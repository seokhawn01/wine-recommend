-- WinePair 데이터베이스 스키마 (PostgreSQL / Supabase)
-- Supabase SQL Editor에서 실행

-- pgvector 확장 활성화 (Supabase에서는 기본 설치됨)
CREATE EXTENSION IF NOT EXISTS vector;

-- 식당 테이블
CREATE TABLE IF NOT EXISTS restaurants (
  restaurant_id  SERIAL PRIMARY KEY,
  name           VARCHAR(100) NOT NULL,
  food_category  VARCHAR(50)  NOT NULL,
  address        VARCHAR(255) NOT NULL,
  corkage_fee    INTEGER      NOT NULL DEFAULT 0,
  corkage_limit  INTEGER      NOT NULL DEFAULT 2,
  reservation_required BOOLEAN NOT NULL DEFAULT FALSE,
  naver_rating   DECIMAL(3,2) NOT NULL DEFAULT 0.00,
  rating         DECIMAL(3,2) NOT NULL DEFAULT 0.00,
  feedback_count INTEGER      NOT NULL DEFAULT 0,
  created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 메뉴 테이블
CREATE TABLE IF NOT EXISTS menus (
  menu_id        SERIAL PRIMARY KEY,
  restaurant_id  INTEGER      NOT NULL,
  name           VARCHAR(100) NOT NULL,
  category       VARCHAR(50)  NOT NULL,
  price          INTEGER      NOT NULL,
  description    TEXT,
  fattiness      DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  umami          DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  spiciness      DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  sweetness      DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  acidity        DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  embedding      vector(1536),
  created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- 와인 테이블
CREATE TABLE IF NOT EXISTS wines (
  wine_id        SERIAL PRIMARY KEY,
  name           VARCHAR(150) NOT NULL,
  grape_variety  VARCHAR(100) NOT NULL,
  region         VARCHAR(100) NOT NULL,
  vintage        INTEGER,
  wine_type      VARCHAR(20)  NOT NULL,
  tannin         DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  acidity        DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  body           DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  sweetness      DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  aroma          VARCHAR(255),
  description    TEXT,
  created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
  user_id          SERIAL PRIMARY KEY,
  email            VARCHAR(255) NOT NULL UNIQUE,
  password_hash    VARCHAR(255) NOT NULL,
  nickname         VARCHAR(50),
  onboarding_done  BOOLEAN NOT NULL DEFAULT FALSE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 취향 프로파일 (사용자당 1개, 최신값)
CREATE TABLE IF NOT EXISTS taste_profiles (
  profile_id           SERIAL PRIMARY KEY,
  user_id              INTEGER NOT NULL UNIQUE,
  pref_tannin          DECIMAL(4,2) NOT NULL DEFAULT 2.50,
  pref_acidity         DECIMAL(4,2) NOT NULL DEFAULT 2.50,
  pref_body            DECIMAL(4,2) NOT NULL DEFAULT 2.50,
  pref_sweetness       DECIMAL(4,2) NOT NULL DEFAULT 2.50,
  preferred_aromas     JSONB,
  dietary_restrictions JSONB,
  embedding            vector(1536),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 취향 변화 이력 (시계열 레이더 차트용)
CREATE TABLE IF NOT EXISTS taste_profile_history (
  history_id     SERIAL PRIMARY KEY,
  user_id        INTEGER NOT NULL,
  feedback_id    INTEGER,
  pref_tannin    DECIMAL(4,2) NOT NULL,
  pref_acidity   DECIMAL(4,2) NOT NULL,
  pref_body      DECIMAL(4,2) NOT NULL,
  pref_sweetness DECIMAL(4,2) NOT NULL,
  change_reason  VARCHAR(100),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 피드백 (좋아요/별로 + 텍스트 후기)
CREATE TABLE IF NOT EXISTS feedbacks (
  feedback_id         SERIAL PRIMARY KEY,
  user_id             INTEGER NOT NULL,
  wine_id             INTEGER NOT NULL,
  menu_id             INTEGER NOT NULL,
  restaurant_id       INTEGER NOT NULL,
  situation           VARCHAR(50),
  reaction            SMALLINT NOT NULL DEFAULT 0,
  review_text         TEXT,
  profile_adjustments JSONB,
  applied             BOOLEAN NOT NULL DEFAULT FALSE,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (wine_id) REFERENCES wines(wine_id),
  FOREIGN KEY (menu_id) REFERENCES menus(menu_id),
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);
