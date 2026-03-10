"""샘플 데이터 적재 — 와인 10종, 식당 5곳, 메뉴 30개"""
from sqlalchemy import text
from connection import get_engine


RESTAURANTS = [
    {
        "name": "라 테이블",
        "food_category": "이탈리안",
        "address": "서울 강남구 역삼로 123",
        "corkage_fee": 30000,
        "corkage_limit": 2,
        "reservation_required": True,
        "naver_rating": 4.5,
        "rating": 4.5,
    },
    {
        "name": "더 스테이크하우스",
        "food_category": "스테이크",
        "address": "서울 서초구 서초대로 456",
        "corkage_fee": 40000,
        "corkage_limit": 2,
        "reservation_required": True,
        "naver_rating": 4.7,
        "rating": 4.7,
    },
    {
        "name": "해운대 해산물",
        "food_category": "해산물",
        "address": "서울 마포구 합정로 789",
        "corkage_fee": 20000,
        "corkage_limit": 3,
        "reservation_required": False,
        "naver_rating": 4.3,
        "rating": 4.3,
    },
    {
        "name": "한우마당",
        "food_category": "한식",
        "address": "서울 종로구 인사동길 55",
        "corkage_fee": 25000,
        "corkage_limit": 2,
        "reservation_required": True,
        "naver_rating": 4.6,
        "rating": 4.6,
    },
    {
        "name": "르 쁘띠 비스트로",
        "food_category": "프렌치",
        "address": "서울 용산구 이태원로 321",
        "corkage_fee": 35000,
        "corkage_limit": 2,
        "reservation_required": True,
        "naver_rating": 4.8,
        "rating": 4.8,
    },
]

WINES = [
    {
        "name": "샤토 마고 2019",
        "grape_variety": "카베르네 소비뇽",
        "region": "프랑스 보르도",
        "vintage": 2019,
        "wine_type": "레드",
        "tannin": 4.5,
        "acidity": 3.5,
        "body": 4.5,
        "sweetness": 1.5,
        "aroma": "블랙커런트, 삼나무, 미네랄, 담배",
        "description": "보르도 1등급 그랑크뤼. 강한 탄닌과 풍부한 과실향이 특징인 풀바디 레드와인.",
    },
    {
        "name": "오퍼스 원 2020",
        "grape_variety": "카베르네 소비뇽 블렌드",
        "region": "미국 나파밸리",
        "vintage": 2020,
        "wine_type": "레드",
        "tannin": 4.0,
        "acidity": 3.5,
        "body": 4.5,
        "sweetness": 2.0,
        "aroma": "블랙베리, 카시스, 모카, 바닐라",
        "description": "나파밸리 대표 카베르네. 벨벳 같은 탄닌과 풍부한 과실미가 조화로운 프리미엄 레드.",
    },
    {
        "name": "부르고뉴 피노 누아 2021",
        "grape_variety": "피노 누아",
        "region": "프랑스 부르고뉴",
        "vintage": 2021,
        "wine_type": "레드",
        "tannin": 2.5,
        "acidity": 4.0,
        "body": 3.0,
        "sweetness": 1.5,
        "aroma": "체리, 라즈베리, 흙냄새, 버섯",
        "description": "섬세한 탄닌과 높은 산미가 특징인 부르고뉴 스타일. 가벼운 미디엄바디.",
    },
    {
        "name": "샤블리 프리미에 크뤼 2022",
        "grape_variety": "샤르도네",
        "region": "프랑스 샤블리",
        "vintage": 2022,
        "wine_type": "화이트",
        "tannin": 0.5,
        "acidity": 4.5,
        "body": 3.0,
        "sweetness": 1.0,
        "aroma": "레몬, 그린애플, 굴껍질, 미네랄",
        "description": "샤블리 특유의 강렬한 미네랄과 높은 산미. 해산물 페어링에 최적화된 화이트.",
    },
    {
        "name": "소비뇽 블랑 말버러 2023",
        "grape_variety": "소비뇽 블랑",
        "region": "뉴질랜드 말버러",
        "vintage": 2023,
        "wine_type": "화이트",
        "tannin": 0.5,
        "acidity": 4.5,
        "body": 2.5,
        "sweetness": 1.5,
        "aroma": "패션프루트, 라임, 허브, 구스베리",
        "description": "열대과일향과 신선한 허브 향이 폭발적. 뉴질랜드 소비뇽 블랑의 전형.",
    },
    {
        "name": "게뷔르츠트라미너 알자스 2022",
        "grape_variety": "게뷔르츠트라미너",
        "region": "프랑스 알자스",
        "vintage": 2022,
        "wine_type": "화이트",
        "tannin": 0.5,
        "acidity": 2.5,
        "body": 3.5,
        "sweetness": 3.5,
        "aroma": "리치, 장미, 생강, 계피",
        "description": "강렬한 꽃향기와 리치 향. 높은 당도로 아시안 스파이시 음식과 잘 어울림.",
    },
    {
        "name": "킴 크로포드 로제 2023",
        "grape_variety": "시라 블렌드",
        "region": "뉴질랜드",
        "vintage": 2023,
        "wine_type": "로제",
        "tannin": 1.5,
        "acidity": 3.5,
        "body": 2.5,
        "sweetness": 2.5,
        "aroma": "딸기, 수박, 복숭아, 장미",
        "description": "신선하고 과일향이 풍부한 드라이 로제. 여름 파티와 가벼운 음식에 어울림.",
    },
    {
        "name": "모에 샹동 브뤼 NV",
        "grape_variety": "샤르도네, 피노 누아, 피노 뮈니에",
        "region": "프랑스 샴페인",
        "vintage": None,
        "wine_type": "스파클링",
        "tannin": 1.0,
        "acidity": 4.0,
        "body": 2.5,
        "sweetness": 1.5,
        "aroma": "빵, 이스트, 사과, 레몬",
        "description": "세계 최대 샴페인 하우스의 대표 브뤼. 섬세한 거품과 이스트 향이 특징.",
    },
    {
        "name": "바롤로 DOCG 2018",
        "grape_variety": "네비올로",
        "region": "이탈리아 피에몬테",
        "vintage": 2018,
        "wine_type": "레드",
        "tannin": 5.0,
        "acidity": 4.5,
        "body": 5.0,
        "sweetness": 1.0,
        "aroma": "타르, 장미, 체리, 가죽, 트러플",
        "description": "이탈리아 와인의 왕. 극강의 탄닌과 산미가 특징. 장기 숙성 필요.",
    },
    {
        "name": "리슬링 슈페트레제 모젤 2021",
        "grape_variety": "리슬링",
        "region": "독일 모젤",
        "vintage": 2021,
        "wine_type": "화이트",
        "tannin": 0.5,
        "acidity": 5.0,
        "body": 2.0,
        "sweetness": 4.0,
        "aroma": "복숭아, 살구, 꿀, 미네랄",
        "description": "독일 모젤의 슈페트레제 리슬링. 극도로 높은 산미와 달콤한 과실향의 완벽한 밸런스.",
    },
]

# 메뉴: 식당별 6개씩 (식당 인덱스 0~4 순서로)
MENUS = [
    # 라 테이블 (이탈리안)
    {"restaurant_idx": 0, "name": "티본스테이크", "category": "메인", "price": 58000,
     "description": "드라이에이징 30일 숙성 티본스테이크. 겉은 바삭, 속은 미디엄레어.",
     "fattiness": 4.5, "umami": 4.0, "spiciness": 0.5, "sweetness": 0.5, "acidity": 0.5},
    {"restaurant_idx": 0, "name": "트러플 파스타", "category": "메인", "price": 32000,
     "description": "블랙 트러플과 파르미지아노 치즈를 넣은 크림 파스타.",
     "fattiness": 3.5, "umami": 4.5, "spiciness": 0.0, "sweetness": 1.0, "acidity": 0.5},
    {"restaurant_idx": 0, "name": "브루스케타", "category": "전채", "price": 14000,
     "description": "토마토와 바질을 올린 이탈리안 전채. 발사믹 글레이즈 드리즐.",
     "fattiness": 1.5, "umami": 2.0, "spiciness": 0.0, "sweetness": 2.0, "acidity": 3.0},
    {"restaurant_idx": 0, "name": "버섯 리조또", "category": "메인", "price": 28000,
     "description": "포르치니 버섯과 트러플 오일을 넣은 크리미 리조또.",
     "fattiness": 3.0, "umami": 4.0, "spiciness": 0.0, "sweetness": 0.5, "acidity": 0.5},
    {"restaurant_idx": 0, "name": "판나코타", "category": "디저트", "price": 12000,
     "description": "바닐라 판나코타에 베리 쿨리를 곁들인 디저트.",
     "fattiness": 3.0, "umami": 0.5, "spiciness": 0.0, "sweetness": 4.5, "acidity": 2.0},
    {"restaurant_idx": 0, "name": "카르파초", "category": "전채", "price": 22000,
     "description": "참치 카르파초. 케이퍼와 레몬 드레싱, 파르미지아노.",
     "fattiness": 2.0, "umami": 3.5, "spiciness": 0.5, "sweetness": 0.5, "acidity": 3.5},

    # 더 스테이크하우스 (스테이크)
    {"restaurant_idx": 1, "name": "안심 스테이크 200g", "category": "메인", "price": 65000,
     "description": "최상급 안심 200g. 미디엄 굽기 권장. 감자 퓨레와 제공.",
     "fattiness": 3.5, "umami": 4.5, "spiciness": 0.0, "sweetness": 0.5, "acidity": 0.5},
    {"restaurant_idx": 1, "name": "립아이 스테이크 300g", "category": "메인", "price": 89000,
     "description": "마블링 최고등급 립아이 300g. 버터 소스와 로즈마리 향.",
     "fattiness": 5.0, "umami": 4.5, "spiciness": 0.0, "sweetness": 0.5, "acidity": 0.5},
    {"restaurant_idx": 1, "name": "포테이토 그라탱", "category": "사이드", "price": 12000,
     "description": "크림과 그뤼에르 치즈로 층층이 쌓은 감자 그라탱.",
     "fattiness": 4.0, "umami": 2.5, "spiciness": 0.0, "sweetness": 1.0, "acidity": 0.5},
    {"restaurant_idx": 1, "name": "시저 샐러드", "category": "전채", "price": 16000,
     "description": "로메인, 파르미지아노, 크루통, 시저 드레싱. 클래식 레시피.",
     "fattiness": 2.5, "umami": 2.5, "spiciness": 0.0, "sweetness": 0.5, "acidity": 2.5},
    {"restaurant_idx": 1, "name": "오닉스 버거", "category": "메인", "price": 28000,
     "description": "200g 패티, 그뤼에르 치즈, 카라멜 양파, 트러플 마요네즈.",
     "fattiness": 4.5, "umami": 4.0, "spiciness": 0.5, "sweetness": 2.0, "acidity": 1.5},
    {"restaurant_idx": 1, "name": "크렘 브륄레", "category": "디저트", "price": 14000,
     "description": "바닐라 크렘 브륄레. 캐러멜 크러스트를 즉석에서 완성.",
     "fattiness": 3.5, "umami": 0.0, "spiciness": 0.0, "sweetness": 5.0, "acidity": 0.5},

    # 해운대 해산물 (해산물)
    {"restaurant_idx": 2, "name": "킹크랩 찜", "category": "메인", "price": 150000,
     "description": "살아있는 킹크랩 1kg 스팀. 간장 소스와 버터 딥핑 소스 제공.",
     "fattiness": 2.0, "umami": 5.0, "spiciness": 0.0, "sweetness": 2.0, "acidity": 1.0},
    {"restaurant_idx": 2, "name": "랍스터 버터구이", "category": "메인", "price": 85000,
     "description": "보스턴 랍스터 반마리 버터 구이. 허브 버터 소스 드리즐.",
     "fattiness": 3.0, "umami": 4.5, "spiciness": 0.0, "sweetness": 2.5, "acidity": 0.5},
    {"restaurant_idx": 2, "name": "굴 6개 세트", "category": "전채", "price": 25000,
     "description": "당일 공수 생굴 6개. 샬롯 비네그레트와 레몬 웨지 제공.",
     "fattiness": 1.5, "umami": 4.0, "spiciness": 0.0, "sweetness": 1.5, "acidity": 3.5},
    {"restaurant_idx": 2, "name": "새우 마늘버터 파스타", "category": "메인", "price": 32000,
     "description": "타이거 새우와 마늘, 화이트 와인 소스 파스타. 알리오 올리오 스타일.",
     "fattiness": 2.5, "umami": 3.5, "spiciness": 1.0, "sweetness": 0.5, "acidity": 2.0},
    {"restaurant_idx": 2, "name": "해산물 그릴 플래터", "category": "메인", "price": 68000,
     "description": "새우, 관자, 오징어, 홍합, 랍스터 테일 모둠 그릴.",
     "fattiness": 2.0, "umami": 4.5, "spiciness": 0.5, "sweetness": 1.5, "acidity": 1.0},
    {"restaurant_idx": 2, "name": "클램 차우더", "category": "수프", "price": 14000,
     "description": "뉴잉글랜드 스타일 조개 크림 수프. 사워도우 브레드 볼 제공.",
     "fattiness": 3.0, "umami": 3.5, "spiciness": 0.0, "sweetness": 1.5, "acidity": 1.0},

    # 한우마당 (한식)
    {"restaurant_idx": 3, "name": "한우 특등심 구이", "category": "메인", "price": 75000,
     "description": "1++ 한우 특등심 150g 숯불구이. 된장찌개, 반찬 포함.",
     "fattiness": 4.5, "umami": 4.5, "spiciness": 0.5, "sweetness": 1.5, "acidity": 0.5},
    {"restaurant_idx": 3, "name": "갈비찜", "category": "메인", "price": 45000,
     "description": "한우 갈비 3시간 이상 저온 조리. 달콤 짭짤한 간장 소스.",
     "fattiness": 3.5, "umami": 4.0, "spiciness": 0.5, "sweetness": 3.5, "acidity": 1.0},
    {"restaurant_idx": 3, "name": "육회 비빔밥", "category": "메인", "price": 22000,
     "description": "신선한 한우 육회를 올린 비빔밥. 달걀 노른자와 참기름 향.",
     "fattiness": 2.5, "umami": 4.0, "spiciness": 2.0, "sweetness": 2.0, "acidity": 1.5},
    {"restaurant_idx": 3, "name": "낙지 볶음", "category": "메인", "price": 28000,
     "description": "쫄깃한 낙지와 채소를 고추장 베이스로 볶은 매운 요리.",
     "fattiness": 1.5, "umami": 3.5, "spiciness": 4.5, "sweetness": 2.0, "acidity": 1.0},
    {"restaurant_idx": 3, "name": "된장찌개", "category": "사이드", "price": 8000,
     "description": "직접 담근 된장으로 끓인 한우 사골 육수 된장찌개.",
     "fattiness": 1.5, "umami": 4.0, "spiciness": 1.0, "sweetness": 0.5, "acidity": 0.5},
    {"restaurant_idx": 3, "name": "전통주 막걸리 세트", "category": "음료", "price": 15000,
     "description": "지역 양조장 생막걸리 2병 세트. 안주 포함.",
     "fattiness": 0.5, "umami": 1.0, "spiciness": 0.0, "sweetness": 3.0, "acidity": 2.5},

    # 르 쁘띠 비스트로 (프렌치)
    {"restaurant_idx": 4, "name": "오리 콩피", "category": "메인", "price": 48000,
     "description": "72시간 저온 조리 오리 다리 콩피. 렌틸콩 퓨레와 제공.",
     "fattiness": 4.5, "umami": 4.0, "spiciness": 0.0, "sweetness": 0.5, "acidity": 1.0},
    {"restaurant_idx": 4, "name": "부야베스", "category": "메인", "price": 52000,
     "description": "마르세유 전통 해산물 수프. 루이유 소스와 바게트 제공.",
     "fattiness": 2.5, "umami": 4.5, "spiciness": 1.0, "sweetness": 1.0, "acidity": 2.0},
    {"restaurant_idx": 4, "name": "에스카르고", "category": "전채", "price": 26000,
     "description": "부르고뉴식 달팽이 구이. 파슬리 마늘 버터와 바게트.",
     "fattiness": 3.5, "umami": 3.5, "spiciness": 0.5, "sweetness": 0.0, "acidity": 0.5},
    {"restaurant_idx": 4, "name": "비프 부르기뇽", "category": "메인", "price": 55000,
     "description": "부르고뉴 레드와인으로 4시간 브레이징한 소고기 스튜.",
     "fattiness": 3.5, "umami": 4.5, "spiciness": 0.0, "sweetness": 2.0, "acidity": 2.0},
    {"restaurant_idx": 4, "name": "포아그라 테린", "category": "전채", "price": 38000,
     "description": "푸아그라 테린 슬라이스. 브리오슈와 피그잼 제공.",
     "fattiness": 5.0, "umami": 4.0, "spiciness": 0.0, "sweetness": 3.0, "acidity": 0.5},
    {"restaurant_idx": 4, "name": "초콜릿 퐁당", "category": "디저트", "price": 16000,
     "description": "뜨거운 쿨바 드 쇼콜라. 바닐라 아이스크림과 제공.",
     "fattiness": 4.0, "umami": 0.5, "spiciness": 0.0, "sweetness": 5.0, "acidity": 0.5},
]


def seed():
    engine = get_engine()

    with engine.begin() as conn:
        # 기존 데이터 초기화 (CASCADE로 외래키 제약 자동 처리)
        if _table_exists(conn, "feedbacks"):
            conn.execute(text("TRUNCATE TABLE feedbacks CASCADE"))
        conn.execute(text("TRUNCATE TABLE menus CASCADE"))
        conn.execute(text("TRUNCATE TABLE wines CASCADE"))
        conn.execute(text("TRUNCATE TABLE restaurants CASCADE"))

        # 식당 삽입 (RETURNING으로 생성된 ID 수집)
        restaurant_ids = []
        for r in RESTAURANTS:
            result = conn.execute(
                text("""
                    INSERT INTO restaurants
                      (name, food_category, address, corkage_fee, corkage_limit,
                       reservation_required, naver_rating, rating)
                    VALUES
                      (:name, :food_category, :address, :corkage_fee, :corkage_limit,
                       :reservation_required, :naver_rating, :rating)
                    RETURNING restaurant_id
                """),
                r,
            )
            restaurant_ids.append(result.fetchone()[0])
        print(f"식당 {len(restaurant_ids)}개 삽입 완료")

        # 와인 삽입
        for w in WINES:
            conn.execute(
                text("""
                    INSERT INTO wines
                      (name, grape_variety, region, vintage, wine_type,
                       tannin, acidity, body, sweetness, aroma, description)
                    VALUES
                      (:name, :grape_variety, :region, :vintage, :wine_type,
                       :tannin, :acidity, :body, :sweetness, :aroma, :description)
                """),
                w,
            )
        print(f"와인 {len(WINES)}개 삽입 완료")

        # 메뉴 삽입
        for m in MENUS:
            restaurant_id = restaurant_ids[m["restaurant_idx"]]
            conn.execute(
                text("""
                    INSERT INTO menus
                      (restaurant_id, name, category, price, description,
                       fattiness, umami, spiciness, sweetness, acidity)
                    VALUES
                      (:restaurant_id, :name, :category, :price, :description,
                       :fattiness, :umami, :spiciness, :sweetness, :acidity)
                """),
                {**m, "restaurant_id": restaurant_id},
            )
        print(f"메뉴 {len(MENUS)}개 삽입 완료")

    print("샘플 데이터 적재 완료!")


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(
        text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :t"),
        {"t": table_name},
    )
    return result.scalar() > 0


if __name__ == "__main__":
    seed()
