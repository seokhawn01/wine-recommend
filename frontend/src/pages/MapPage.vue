<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { restaurants } from '@/mock/data'
import Badge from '@/components/ui/badge/Badge.vue'
import { Search, Star, MapPin, ChevronRight, SlidersHorizontal } from 'lucide-vue-next'

const router = useRouter()
const searchQuery = ref('')
const selectedCategory = ref('전체')

const categories = ['전체', '양식', '이탈리안', '한식', '해산물', '프렌치']

const filtered = computed(() => {
  let list = restaurants
  if (selectedCategory.value !== '전체') {
    list = list.filter((r) => r.category === selectedCategory.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q)
    )
  }
  return list
})

const categoryEmoji = {
  '양식': '🥩', '이탈리안': '🍝', '한식': '🍖',
  '해산물': '🦞', '프렌치': '🥐', '일식': '🍣',
}
</script>

<template>
  <div class="flex flex-col min-h-screen bg-[#FFF8F0]">
    <!-- 헤더 -->
    <header class="px-5 pt-12 pb-3">
      <h1 class="text-lg font-bold text-[#722F37] mb-3">📍 근처 콜키지 식당</h1>

      <!-- 검색창 -->
      <div class="relative">
        <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="식당 이름, 카테고리 검색"
          class="w-full h-10 pl-9 pr-4 text-sm bg-white rounded-xl border border-gray-200 outline-none focus:border-[#722F37] transition"
        />
      </div>
    </header>

    <!-- 카테고리 칩 가로 스크롤 -->
    <div class="flex gap-2 overflow-x-auto px-5 pb-3 scrollbar-none">
      <button
        v-for="cat in categories"
        :key="cat"
        :class="[
          'shrink-0 text-xs font-semibold px-3.5 py-1.5 rounded-full border transition',
          selectedCategory === cat
            ? 'bg-[#722F37] text-white border-[#722F37]'
            : 'bg-white text-gray-600 border-gray-200'
        ]"
        @click="selectedCategory = cat"
      >
        {{ cat }}
      </button>
    </div>

    <!-- 지도 플레이스홀더 -->
    <div class="mx-5 mb-3 rounded-2xl overflow-hidden shadow-sm bg-gray-200 h-[200px] relative flex items-center justify-center">
      <div class="text-center text-gray-500 z-10">
        <div class="text-4xl mb-1">🗺️</div>
        <p class="text-sm font-medium">네이버 지도</p>
        <p class="text-xs text-gray-400">API 키 설정 후 활성화</p>
      </div>
      <!-- Mock 마커들 -->
      <div
        v-for="(r, i) in filtered.slice(0, 4)"
        :key="r.id"
        :style="{ top: `${20 + i * 18}%`, left: `${15 + i * 20}%` }"
        class="absolute w-7 h-7 bg-[#722F37] rounded-full border-2 border-white shadow-md flex items-center justify-center"
      >
        <span class="text-white text-xs font-bold">{{ i + 1 }}</span>
      </div>
    </div>

    <!-- 결과 건수 + 필터 -->
    <div class="flex items-center justify-between px-5 mb-2">
      <p class="text-xs text-gray-500 font-medium">
        {{ filtered.length }}개 식당
      </p>
      <button class="flex items-center gap-1 text-xs text-gray-500 bg-white px-3 py-1.5 rounded-lg border border-gray-200 shadow-sm">
        <SlidersHorizontal :size="13" />
        필터
      </button>
    </div>

    <!-- 식당 목록 -->
    <div class="flex-1 px-5 space-y-2.5 pb-6">
      <div
        v-for="restaurant in filtered"
        :key="restaurant.id"
        class="bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3 cursor-pointer active:bg-gray-50 transition"
        @click="router.push(`/restaurant/${restaurant.id}`)"
      >
        <div class="w-12 h-12 bg-[#FFF8F0] rounded-xl flex items-center justify-center shrink-0 text-2xl">
          {{ categoryEmoji[restaurant.category] || '🍽️' }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-gray-900 truncate">{{ restaurant.name }}</p>
          <div class="flex items-center gap-2 mt-0.5">
            <div class="flex items-center gap-0.5">
              <Star :size="11" class="text-[#C5A028] fill-[#C5A028]" />
              <span class="text-xs text-gray-600">{{ restaurant.rating }}</span>
            </div>
            <span class="text-gray-300 text-xs">·</span>
            <div class="flex items-center gap-0.5">
              <MapPin :size="11" class="text-gray-400" />
              <span class="text-xs text-gray-400">{{ restaurant.distance }}</span>
            </div>
          </div>
          <div class="mt-1.5 flex gap-1.5 flex-wrap">
            <Badge
              :variant="restaurant.corkageFee === 0 ? 'default' : 'secondary'"
              class="text-[10px] h-4 px-1.5"
            >
              {{ restaurant.corkageFee === 0 ? '콜키지 무료' : `${restaurant.corkageFee.toLocaleString()}원` }}
            </Badge>
            <Badge
              v-if="restaurant.reservationRequired"
              variant="outline"
              class="text-[10px] h-4 px-1.5"
            >
              예약필수
            </Badge>
          </div>
        </div>
        <ChevronRight :size="16" class="text-gray-300 shrink-0" />
      </div>

      <div v-if="filtered.length === 0" class="py-16 text-center text-gray-400">
        <div class="text-4xl mb-2">🔍</div>
        <p class="text-sm">검색 결과가 없습니다</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }
</style>
