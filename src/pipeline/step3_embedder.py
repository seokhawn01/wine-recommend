"""STEP 3: OpenAI text-embedding-3-small 임베딩"""
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()


def get_embeddings() -> OpenAIEmbeddings:
    """OpenAI 임베딩 모델 반환 (text-embedding-3-small, 1536차원)"""
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    return embeddings


if __name__ == "__main__":
    embeddings = get_embeddings()
    # 연결 테스트
    test_vector = embeddings.embed_query("카베르네 소비뇽 탄닌 지방성 페어링")
    print(f"[STEP 3] 임베딩 차원: {len(test_vector)}")
    print(f"[STEP 3] 첫 5개 값: {test_vector[:5]}")
