<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTasteStore } from '@/stores/taste'
import { wines, restaurants } from '@/mock/data'
import TasteNebulaChart from '@/components/chart/TasteNebulaChart.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Bell, ChevronRight, MapPin, Star, Wine } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const tasteStore = useTasteStore()

// 취향 기반 와인 점수: 각 속성 차이의 역수
function matchScore(wine) {
  const diff =
    Math.abs(wine.tannin - tasteStore.tannin) +
    Math.abs(wine.acidity - tasteStore.acidity) +
    Math.abs(wine.body - tasteStore.body) +
    Math.abs(wine.sweetness - tasteStore.sweetness)
  return 1 / (1 + diff)
}

const recommendedWines = computed(() =>
  [...wines].sort((a, b) => matchScore(b) - matchScore(a)).slice(0, 5)
)

// 콜키지 무료 식당 우선 정렬
const nearbyRestaurants = computed(() =>
  [...restaurants].sort((a, b) => a.corkageFee - b.corkageFee).slice(0, 4)
)

const nickname = computed(() => authStore.user?.nickname || '게스트')

// 탭: 메뉴→와인 / 와인→메뉴
const activeTab = ref('menuToWine')

// 와인 타입 색상
const typeColor = {
  red: 'bg-[#722F37] text-white',
  white: 'bg-[#C5A028] text-white',
  sparkling: 'bg-blue-400 text-white',
  rosé: 'bg-pink-400 text-white',
}
const typeLabel = { red: '레드', white: '화이트', sparkling: '스파클링', rosé: '로제' }
</script>

<template>
  <div class="min-h-screen bg-[#FFF8F0]">
    <!-- 상단 헤더 -->
    <header class="flex items-center justify-between px-5 pt-12 pb-4">
      <div>
        <p class="text-xs text-gray-400 font-medium">나의 와인 취향</p>
        <h1 class="text-lg font-bold text-[#722F37]">
          {{ nickname }}님의 와인 성운 🍷
        </h1>
      </div>
      <button class="relative p-2 rounded-full bg-white shadow-sm" aria-label="알림">
        <Bell :size="20" class="text-gray-500" />
      </button>
    </header>

    <!-- ① 취향 성운 섹션 -->
    <section class="flex flex-col items-center px-5 pb-2">
      <TasteNebulaChart
        :tannin="tasteStore.tannin"
        :acidity="tasteStore.acidity"
        :body="tasteStore.body"
        :sweetness="tasteStore.sweetness"
        :size="280"
      />

      <!-- 4가지 취향 수치 태그 -->
      <div class="flex flex-wrap justify-center gap-2 mt-3">
        <span
          v-for="item in [
            { label: '타닌', value: tasteStore.tannin, color: 'bg-purple-100 text-purple-700' },
            { label: '산미', value: tasteStore.acidity, color: 'bg-blue-100 text-blue-700' },
            { label: '바디', value: tasteStore.body, color: 'bg-rose-100 text-rose-700' },
            { label: '당도', value: tasteStore.sweetness, color: 'bg-amber-100 text-amber-700' },
          ]"
          :key="item.label"
          :class="['text-xs font-semibold px-3 py-1 rounded-full', item.color]"
        >
          {{ item.label }} {{ item.value.toFixed(1) }}
        </span>
      </div>

      <button
        class="mt-3 text-xs text-[#722F37] font-medium flex items-center gap-0.5"
        @click="router.push('/onboarding')"
      >
        취향 재설정 <ChevronRight :size="14" />
      </button>
    </section>

    <!-- ② 추천 기능 탭 -->
    <section class="px-5 mt-2">
      <div class="flex bg-white rounded-2xl p-1 shadow-sm gap-1">
        <button
          :class="[
            'flex-1 py-2.5 text-xs font-semibold rounded-xl transition-all',
            activeTab === 'menuToWine'
              ? 'bg-[#722F37] text-white shadow-sm'
              : 'text-gray-500'
          ]"
          @click="activeTab = 'menuToWine'"
        >
          🍽️ 메뉴 → 와인
        </button>
        <button
          :class="[
            'flex-1 py-2.5 text-xs font-semibold rounded-xl transition-all',
            activeTab === 'wineToMenu'
              ? 'bg-[#722F37] text-white shadow-sm'
              : 'text-gray-500'
          ]"
          @click="activeTab = 'wineToMenu'"
        >
          🍾 내 와인 → 메뉴
        </button>
      </div>

      <!-- 메뉴→와인 CTA -->
      <div v-if="activeTab === 'menuToWine'" class="mt-3">
        <button
          class="w-full bg-white rounded-2xl p-4 shadow-sm flex items-center justify-between border border-dashed border-[#722F37]/30 active:bg-[#FFF0F0] transition"
          @click="router.push('/home')"
        >
          <div class="text-left">
            <p class="text-sm font-semibold text-gray-800">식당 메뉴에 맞는 와인 추천</p>
            <p class="text-xs text-gray-400 mt-0.5">콜키지 식당 선택 → 메뉴 선택 → AI 추천</p>
          </div>
          <div class="w-10 h-10 bg-[#722F37] rounded-full flex items-center justify-center shrink-0">
            <Wine :size="20" class="text-white" />
          </div>
        </button>
      </div>

      <!-- 내 와인→메뉴 CTA -->
      <div v-else class="mt-3">
        <button
          class="w-full bg-white rounded-2xl p-4 shadow-sm flex items-center justify-between border border-dashed border-[#C5A028]/50 active:bg-[#FFFBF0] transition"
          @click="router.push('/mypage')"
        >
          <div class="text-left">
            <p class="text-sm font-semibold text-gray-800">내 와인에 맞는 메뉴 추천</p>
            <p class="text-xs text-gray-400 mt-0.5">내 컬렉션 선택 → 식당/메뉴 AI 추천</p>
          </div>
          <div class="w-10 h-10 bg-[#C5A028] rounded-full flex items-center justify-center shrink-0">
            <span class="text-white text-xl">🍾</span>
          </div>
        </button>
      </div>
    </section>

    <!-- ③ 취향 맞춤 와인 추천 -->
    <section class="mt-6">
      <div class="flex items-center justify-between px-5 mb-3">
        <h2 class="text-sm font-bold text-gray-800">✨ 내 취향의 와인</h2>
        <button class="text-xs text-[#722F37] flex items-center gap-0.5">
          전체 보기 <ChevronRight :size="13" />
        </button>
      </div>

      <!-- 가로 스크롤 와인 카드 -->
      <div class="flex gap-3 overflow-x-auto px-5 pb-3 scrollbar-none snap-x snap-mandatory">
        <div
          v-for="wine in recommendedWines"
          :key="wine.id"
          class="shrink-0 w-36 bg-white rounded-2xl p-4 shadow-sm snap-start cursor-pointer active:scale-[0.97] transition"
          @click="router.push(`/mypage`)"
        >
          <!-- 와인 타입 배지 -->
          <div class="flex items-center justify-between mb-3">
            <span :class="['text-[10px] font-bold px-2 py-0.5 rounded-full', typeColor[wine.type] || 'bg-gray-200 text-gray-600']">
              {{ typeLabel[wine.type] || wine.type }}
            </span>
            <div class="flex items-center gap-0.5">
              <Star :size="11" class="text-[#C5A028] fill-[#C5A028]" />
              <span class="text-[10px] text-gray-500">{{ (matchScore(wine) * 100).toFixed(0) }}%</span>
            </div>
          </div>

          <!-- 와인 이름 -->
          <p class="text-xs font-bold text-gray-900 leading-tight mb-1 line-clamp-2">{{ wine.name }}</p>
          <p class="text-[10px] text-gray-400 mb-3">{{ wine.region }}</p>

          <!-- 취향 미니 바 -->
          <div class="space-y-1">
            <div v-for="bar in [
              { label: '타닌', val: wine.tannin },
              { label: '산미', val: wine.acidity },
            ]" :key="bar.label" class="flex items-center gap-1.5">
              <span class="text-[9px] text-gray-400 w-5">{{ bar.label }}</span>
              <div class="flex-1 h-1 bg-gray-100 rounded-full">
                <div
                  class="h-1 bg-[#722F37] rounded-full"
                  :style="{ width: `${(bar.val / 5) * 100}%` }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ④ 이 와인을 즐길 근처 식당 -->
    <section class="mt-4 px-5 mb-6">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-bold text-gray-800">📍 근처 콜키지 식당</h2>
        <button class="text-xs text-[#722F37] flex items-center gap-0.5" @click="router.push('/map')">
          지도로 보기 <ChevronRight :size="13" />
        </button>
      </div>

      <div class="space-y-2.5">
        <div
          v-for="restaurant in nearbyRestaurants"
          :key="restaurant.id"
          class="bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3 cursor-pointer active:bg-gray-50 transition"
          @click="router.push(`/restaurant/${restaurant.id}`)"
        >
          <!-- 아이콘 -->
          <div class="w-12 h-12 bg-[#FFF8F0] rounded-xl flex items-center justify-center shrink-0">
            <span class="text-2xl">
              {{ { '양식': '🥩', '이탈리안': '🍝', '한식': '🍖', '해산물': '🦞', '프렌치': '🥐', '일식': '🍣' }[restaurant.category] || '🍽️' }}
            </span>
          </div>

          <!-- 정보 -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-gray-900 truncate">{{ restaurant.name }}</p>
            <div class="flex items-center gap-2 mt-0.5">
              <div class="flex items-center gap-0.5">
                <Star :size="11" class="text-[#C5A028] fill-[#C5A028]" />
                <span class="text-xs text-gray-600">{{ restaurant.rating }}</span>
              </div>
              <span class="text-gray-300">·</span>
              <div class="flex items-center gap-0.5">
                <MapPin :size="11" class="text-gray-400" />
                <span class="text-xs text-gray-400">{{ restaurant.distance }}</span>
              </div>
            </div>
            <!-- 콜키지 뱃지 -->
            <div class="mt-1.5">
              <Badge
                :variant="restaurant.corkageFee === 0 ? 'default' : 'secondary'"
                class="text-[10px] h-4 px-1.5"
              >
                {{ restaurant.corkageFee === 0 ? '콜키지 무료' : `콜키지 ${restaurant.corkageFee.toLocaleString()}원` }}
              </Badge>
            </div>
          </div>

          <ChevronRight :size="16" class="text-gray-300 shrink-0" />
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }
</style>
