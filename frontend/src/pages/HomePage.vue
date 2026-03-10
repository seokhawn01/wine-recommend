<script setup>
import { ref, computed } from 'vue'
import { restaurants } from '@/mock/data'
import RestaurantCard from '@/components/restaurant/RestaurantCard.vue'
import Input from '@/components/ui/input/Input.vue'
import Badge from '@/components/ui/badge/Badge.vue'

const searchQuery = ref('')
const selectedCategory = ref('전체')
const selectedSort = ref('distance')

const categories = ['전체', '양식', '이탈리안', '한식', '해산물', '프렌치', '일식']

const filteredRestaurants = computed(() => {
  let result = restaurants
  if (selectedCategory.value !== '전체') {
    result = result.filter((r) => r.category === selectedCategory.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q) ||
        r.address.toLowerCase().includes(q)
    )
  }
  return result
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- 페이지 헤더 -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">주변 콜키지 식당</h1>
        <p class="text-gray-500 text-sm">내 와인을 가져갈 수 있는 콜키지 허용 식당을 찾아보세요.</p>
      </div>

      <!-- 검색 + 필터 영역 -->
      <div class="flex flex-col lg:flex-row gap-4 mb-6">
        <div class="relative flex-1">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <Input
            v-model="searchQuery"
            placeholder="식당 이름, 위치, 카테고리 검색"
            class="pl-9 h-10 bg-white"
          />
        </div>
        <div class="flex gap-2 flex-wrap">
          <Badge
            v-for="cat in categories"
            :key="cat"
            :variant="selectedCategory === cat ? 'default' : 'unselected'"
            class="shrink-0 cursor-pointer py-2 px-4 text-sm border-0 h-10 flex items-center"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </Badge>
        </div>
      </div>

      <!-- 메인 컨텐츠: 지도 + 목록 -->
      <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
        <!-- 지도 영역 (왼쪽 3/5) -->
        <div class="xl:col-span-3">
          <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
            <div class="bg-gray-200 h-[480px] flex items-center justify-center relative">
              <div class="text-center text-gray-500">
                <div class="text-5xl mb-2">🗺️</div>
                <p class="text-base font-medium">네이버 지도</p>
                <p class="text-sm text-gray-400">API 키 설정 후 활성화</p>
              </div>
              <!-- Mock 마커들 -->
              <div class="absolute top-12 left-16 w-7 h-7 bg-[#722F37] rounded-full border-2 border-white shadow-md flex items-center justify-center">
                <span class="text-white text-xs font-bold">1</span>
              </div>
              <div class="absolute top-24 left-1/2 w-7 h-7 bg-[#722F37] rounded-full border-2 border-white shadow-md flex items-center justify-center">
                <span class="text-white text-xs font-bold">2</span>
              </div>
              <div class="absolute bottom-20 right-20 w-7 h-7 bg-[#722F37] rounded-full border-2 border-white shadow-md flex items-center justify-center">
                <span class="text-white text-xs font-bold">3</span>
              </div>
              <div class="absolute top-1/3 right-1/3 w-7 h-7 bg-[#722F37] rounded-full border-2 border-white shadow-md flex items-center justify-center">
                <span class="text-white text-xs font-bold">4</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 식당 목록 (오른쪽 2/5) -->
        <div class="xl:col-span-2">
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-semibold text-gray-900">
              {{ selectedCategory === '전체' ? '전체 식당' : selectedCategory }}
              <span class="text-sm font-normal text-gray-400 ml-1">{{ filteredRestaurants.length }}곳</span>
            </h2>
            <select
              v-model="selectedSort"
              class="text-xs text-gray-600 border border-gray-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-[#722F37]"
            >
              <option value="distance">거리순</option>
              <option value="rating">별점순</option>
            </select>
          </div>

          <div v-if="filteredRestaurants.length" class="space-y-3 max-h-[440px] overflow-y-auto pr-1">
            <RestaurantCard
              v-for="restaurant in filteredRestaurants"
              :key="restaurant.id"
              :restaurant="restaurant"
              layout="horizontal"
            />
          </div>
          <div v-else class="py-20 text-center text-gray-400">
            <div class="text-4xl mb-2">🔍</div>
            <p class="text-sm">검색 결과가 없습니다.</p>
          </div>
        </div>
      </div>

      <!-- 하단: 전체 그리드 뷰 -->
      <div class="mt-10">
        <h2 class="font-bold text-gray-900 text-lg mb-4">
          모든 콜키지 식당
          <span class="text-sm font-normal text-gray-400 ml-1">{{ filteredRestaurants.length }}곳</span>
        </h2>
        <div v-if="filteredRestaurants.length" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <RestaurantCard
            v-for="restaurant in filteredRestaurants"
            :key="`grid-${restaurant.id}`"
            :restaurant="restaurant"
          />
        </div>
      </div>
    </div>
  </div>
</template>
