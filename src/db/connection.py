"""PostgreSQL (Supabase) SQLAlchemy 연결 모듈"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()


def get_engine():
    """SQLAlchemy 엔진 생성 (DATABASE_URL 우선, 없으면 개별 변수 조합)"""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        url = database_url
    else:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME", "postgres")
        url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"

    engine = create_engine(url, echo=False)
    return engine


def get_session():
    """SQLAlchemy 세션 생성"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def test_connection():
    """DB 연결 테스트"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("PostgreSQL 연결 성공:", result.fetchone())
        return True
    except Exception as e:
        print(f"PostgreSQL 연결 실패: {e}")
        return False


if __name__ == "__main__":
    test_connection()
