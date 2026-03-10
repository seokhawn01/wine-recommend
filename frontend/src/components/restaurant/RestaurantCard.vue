<script setup>
import { useRouter } from 'vue-router'
import Badge from '@/components/ui/badge/Badge.vue'

const router = useRouter()
defineProps({
  restaurant: {
    type: Object,
    required: true,
  },
  // 'card' (기본 그리드) | 'horizontal' (사이드바 목록)
  layout: {
    type: String,
    default: 'card',
  },
})
</script>

<template>
  <!-- 가로형 (사이드바 목록) -->
  <div
    v-if="layout === 'horizontal'"
    class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition-shadow flex"
    @click="router.push(`/restaurant/${restaurant.id}`)"
  >
    <!-- 왼쪽 이미지 -->
    <div class="w-20 shrink-0 bg-gradient-to-br from-[#FFF8F0] to-[#F5E8D8] flex items-center justify-center">
      <span class="text-3xl">🍽️</span>
    </div>
    <!-- 오른쪽 정보 -->
    <div class="flex-1 p-3 min-w-0">
      <div class="flex items-start justify-between gap-2 mb-1">
        <h3 class="font-semibold text-gray-900 text-sm leading-tight truncate">{{ restaurant.name }}</h3>
        <div class="flex items-center gap-0.5 shrink-0">
          <span class="text-yellow-400 text-xs">★</span>
          <span class="text-xs font-medium text-gray-700">{{ restaurant.rating }}</span>
        </div>
      </div>
      <p class="text-xs text-gray-500 mb-1.5">{{ restaurant.category }} · {{ restaurant.distance }}</p>
      <div class="flex items-center gap-1.5">
        <Badge v-if="restaurant.corkageFee === 0" variant="gold" class="text-xs">무료</Badge>
        <Badge v-else variant="secondary" class="text-xs">{{ restaurant.corkageFee.toLocaleString() }}원</Badge>
        <Badge v-if="restaurant.reservationRequired" variant="secondary" class="text-xs">예약 필수</Badge>
      </div>
    </div>
  </div>

  <!-- 카드형 (기본 그리드) -->
  <div
    v-else
    class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition-shadow active:scale-[0.99]"
    @click="router.push(`/restaurant/${restaurant.id}`)"
  >
    <!-- 이미지 영역 -->
    <div class="h-36 bg-gradient-to-br from-[#FFF8F0] to-[#F5E8D8] relative flex items-center justify-center">
      <span class="text-5xl">🍽️</span>
      <!-- 콜키지 배지 -->
      <div class="absolute top-2 right-2">
        <Badge v-if="restaurant.corkageFee === 0" variant="gold" class="text-xs">콜키지 무료</Badge>
        <Badge v-else variant="secondary" class="text-xs">콜키지 {{ restaurant.corkageFee.toLocaleString() }}원</Badge>
      </div>
    </div>

    <!-- 정보 영역 -->
    <div class="p-3">
      <div class="flex items-start justify-between mb-1">
        <h3 class="font-semibold text-gray-900 text-sm leading-tight">{{ restaurant.name }}</h3>
        <div class="flex items-center gap-0.5 ml-2 shrink-0">
          <span class="text-yellow-400 text-sm">★</span>
          <span class="text-xs font-medium text-gray-700">{{ restaurant.rating }}</span>
          <span class="text-xs text-gray-400">({{ restaurant.feedbackCount }})</span>
        </div>
      </div>

      <div class="flex items-center gap-2 text-xs text-gray-500 mb-2">
        <span>{{ restaurant.category }}</span>
        <span>·</span>
        <span>{{ restaurant.distance }}</span>
        <span v-if="restaurant.reservationRequired" class="text-orange-500">· 예약 필수</span>
      </div>

      <div class="flex flex-wrap gap-1">
        <Badge
          v-for="tag in restaurant.tags.slice(0, 3)"
          :key="tag"
          variant="secondary"
          class="text-xs"
        >
          {{ tag }}
        </Badge>
      </div>
    </div>
  </div>
</template>
