# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 명령어

```bash
npm run dev       # 개발 서버 (기본 http://localhost:5173, 포트 충돌 시 5174)
npm run build     # 프로덕션 빌드 → dist/
npm run preview   # 빌드 결과 로컬 미리보기
npm run lint      # oxlint + eslint 순서로 실행 (--fix 포함)
```

## 아키텍처

### 전체 흐름

```
App.vue (전체 화면 웹 레이아웃 — max-w-[390px] 제거됨)
  ├── Navbar.vue (sticky top, 인증/온보딩 페이지에서는 숨김)
  └── RouterView
        ├── pages/          ← 라우트 단위 페이지
        ├── components/     ← 재사용 컴포넌트
        └── stores/         ← Pinia 전역 상태
```

### 라우트 구조 (`src/router/index.js`)

| 경로 | 페이지 |
|------|--------|
| `/home` | HomePage — 식당 목록, 검색/필터 |
| `/restaurant/:id` | RestaurantDetailPage — 와인 선택 + 메뉴 ★ 페어링 |
| `/match` | AiMatchPage — AI 소믈리에 추천 결과 + 피드백 |
| `/onboarding` | OnboardingPage — 2스텝 취향 설정 (슬라이더 → 향/식이제한) |
| `/mypage` | MyPage — 취향 레이더 차트 + 와인 컬렉션 |
| `/wine/register` | WineRegisterPage — OCR 탭 / 수동 입력 탭 |
| `/login`, `/signup` | 인증 페이지 |

### Pinia 스토어 (`src/stores/`)

- **`auth.js`**: `user`, `isLoggedIn`, `isOnboardingDone`. 현재 Mock 구현 — 백엔드 연동 시 Supabase Auth로 교체
- **`taste.js`**: 탄닌/산미/바디/당도(0~5), 선호향 배열, 식이제한 배열. `getRadarData()`로 Chart.js 형식 반환

### UI 컴포넌트 (`src/components/ui/`)

shadcn-vue CLI 미사용 — **컴포넌트 직접 구현** (radix-vue + class-variance-authority + clsx + tailwind-merge).
새 컴포넌트 추가 시 같은 패턴으로 직접 작성할 것. `shadcn-vue add` 명령어는 TailwindCSS v4와 호환 안 됨.

- `Button`: `variant` prop (default/outline/secondary/ghost/link/gold)
- `Badge`: `variant` prop (default/secondary/outline/gold/green/gray/selected/unselected)
- `Tabs`: `provide/inject` 방식 — `Tabs` → `TabsList/TabsTrigger/TabsContent` 조합
- `Slider`: 커스텀 range input, `modelValue` + `@update:modelValue` v-model 패턴
- `Select`: 네이티브 `<select>` 래핑, `placeholder` prop 지원

### 비즈니스 컴포넌트

- **`TasteRadarChart.vue`**: vue-chartjs `Radar`. `tannin/acidity/body/sweetness` props를 직접 받음 (스토어 불포함)
- **`RestaurantCard.vue`**: 식당 카드. `layout` prop으로 `'card'`(그리드 기본) / `'horizontal'`(사이드바 목록) 두 가지 레이아웃 지원. `corkageFee === 0` 조건으로 "콜키지 무료" 배지 분기
- **`Navbar.vue`**: 웹 상단 네비게이션. 로고(좌) + 홈/AI매칭(중) + 마이페이지/로그아웃(우). 인증·온보딩 페이지에서 App.vue가 조건부로 숨김
- **`MenuPairingItem.vue`**: `pairingScore` 기준 ≥0.8=금★, ≥0.5=은★, 미만=회색★

### Mock 데이터 (`src/mock/data.js`)

백엔드 API 미연동 상태에서 모든 페이지가 이 파일의 데이터로 동작함.
API 연동 시 각 페이지/스토어에서 import를 API 호출로 교체.

```js
export { restaurants, wines, menus, situations, aromas, dietaryRestrictions, mockUserProfile, mockAiRecommendation }
```

### CSS / 디자인 시스템

TailwindCSS v4 — `tailwind.config.js` 없음. `src/assets/index.css`에 `@import "tailwindcss"` 및 CSS 변수 정의.

| 토큰 | 값 |
|------|----|
| Primary (버건디) | `#722F37` |
| Cream | `#FFF8F0` |
| Gold | `#C5A028` |

Tailwind 클래스에서 커스텀 색상 사용 시 `text-[#722F37]`, `bg-[#FFF8F0]` 형태로 직접 입력.

### 유틸리티

- `src/lib/utils.js`: `cn(...inputs)` — clsx + tailwind-merge 조합
- `@` alias: `src/` 디렉토리 절대 경로 (`@/components/...`)

## 중요 주의사항

- **현재 전체 Mock 상태**: auth, 식당 목록, 메뉴, AI 추천 모두 Mock. 실제 API 연동 전까지 `src/mock/data.js` 데이터 사용
- **AiMatchPage**: `/match?restaurantId=1&wineId=1&situation=date` 쿼리 파라미터로 컨텍스트 전달받음. RestaurantDetailPage에서 라우팅
- **웹 우선 레이아웃**: 모든 페이지 `max-w-7xl mx-auto px-6` 컨테이너 기준. 그리드는 `grid-cols-1 lg:grid-cols-N` 반응형 적용. `BottomNav.vue` 미사용 (파일 유지, 임포트 없음)
- **Tabs 컴포넌트**: `provide/inject` 기반이므로 반드시 `<Tabs>` 안에 `<TabsTrigger>`, `<TabsContent>` 위치해야 함. `defaultValue` 또는 `modelValue` 중 하나 전달 필요
