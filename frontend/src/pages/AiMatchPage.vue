<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { wines, restaurants, situations, mockAiRecommendation } from '@/mock/data'
import WineCard from '@/components/wine/WineCard.vue'
import MenuPairingItem from '@/components/restaurant/MenuPairingItem.vue'
import Button from '@/components/ui/button/Button.vue'
import Textarea from '@/components/ui/textarea/Textarea.vue'
import Skeleton from '@/components/ui/skeleton/Skeleton.vue'
import Badge from '@/components/ui/badge/Badge.vue'

const route = useRoute()
const router = useRouter()

const isLoading = ref(true)
const recommendation = ref(null)
const feedbackGiven = ref(null) // null | 'like' | 'dislike'
const reviewText = ref('')
const showReviewInput = ref(false)

const wineId = parseInt(route.query.wineId)
const restaurantId = parseInt(route.query.restaurantId)
const situation = route.query.situation

const selectedWine = wines.find((w) => w.id === wineId) || wines[0]
const selectedRestaurant = restaurants.find((r) => r.id === restaurantId)
const situationLabel = situations.find((s) => s.value === situation)?.label || ''

onMounted(() => {
  // AI 추천 로딩 시뮬레이션
  setTimeout(() => {
    recommendation.value = {
      ...mockAiRecommendation,
      wine: selectedWine || mockAiRecommendation.wine,
    }
    isLoading.value = false
  }, 1500)
})

function handleFeedback(type) {
  feedbackGiven.value = type
  showReviewInput.value = true
}

function submitReview() {
  // Mock 저장
  showReviewInput.value = false
  router.push('/home')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 페이지 헤더 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
        <button
          class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
          @click="router.back()"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          식당으로
        </button>
        <span class="text-gray-300">/</span>
        <span class="text-sm text-gray-800 font-medium">AI 페어링 추천</span>
      </div>
    </div>

    <div class="max-w-5xl mx-auto px-6 py-8">
      <!-- 컨텍스트 배지 -->
      <div class="flex flex-wrap gap-2 mb-6">
        <Badge v-if="selectedRestaurant" variant="secondary" class="text-sm py-1.5 px-3">
          🏠 {{ selectedRestaurant.name }}
        </Badge>
        <Badge v-if="situationLabel" variant="secondary" class="text-sm py-1.5 px-3">
          ✨ {{ situationLabel }}
        </Badge>
      </div>

      <!-- 로딩 스켈레톤 -->
      <div v-if="isLoading">
        <div class="text-center mb-8">
          <div class="w-10 h-10 border-3 border-[#722F37] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p class="text-gray-500">AI 소믈리에가 최적의 페어링을 분석하고 있습니다...</p>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <Skeleton class="h-5 w-1/3 mb-4" />
            <Skeleton class="h-32 w-full mb-3" />
            <Skeleton class="h-4 w-full mb-2" />
            <Skeleton class="h-4 w-5/6" />
          </div>
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <Skeleton class="h-5 w-1/2 mb-4" />
            <Skeleton class="h-4 w-full mb-2" />
            <Skeleton class="h-4 w-full mb-2" />
            <Skeleton class="h-4 w-4/5" />
          </div>
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <Skeleton class="h-5 w-1/3 mb-4" />
            <Skeleton class="h-16 w-full mb-2" />
            <Skeleton class="h-16 w-full" />
          </div>
        </div>
      </div>

      <!-- 추천 결과 -->
      <div v-else-if="recommendation">
        <!-- 3열 그리드 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <!-- 1열: 선택 와인 -->
          <div>
            <h2 class="font-bold text-gray-700 mb-3">🍷 선택하신 와인</h2>
            <WineCard :wine="recommendation.wine" />
          </div>

          <!-- 2열: AI 소믈리에 설명 -->
          <div>
            <h2 class="font-bold text-gray-700 mb-3">🤖 소믈리에 추천</h2>
            <div class="bg-white rounded-xl p-5 shadow-sm h-full">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 bg-[#722F37] rounded-full flex items-center justify-center shrink-0">
                  <span class="text-white text-sm font-bold">AI</span>
                </div>
                <div>
                  <p class="font-semibold text-gray-900 text-sm">AI 소믈리에</p>
                  <div class="flex items-center gap-1.5 mt-0.5">
                    <span class="text-xs text-gray-400">신뢰도</span>
                    <div class="w-20 h-1.5 bg-gray-100 rounded-full">
                      <div
                        class="h-1.5 bg-[#722F37] rounded-full transition-all"
                        :style="{ width: `${recommendation.confidence * 100}%` }"
                      />
                    </div>
                    <span class="text-xs text-[#722F37] font-semibold">{{ Math.round(recommendation.confidence * 100) }}%</span>
                  </div>
                </div>
              </div>
              <p class="text-sm text-gray-700 leading-relaxed">{{ recommendation.explanation }}</p>
            </div>
          </div>

          <!-- 3열: 추천 메뉴 -->
          <div>
            <h2 class="font-bold text-gray-700 mb-3">🍽️ 추천 메뉴</h2>
            <div class="bg-white rounded-xl shadow-sm overflow-hidden">
              <MenuPairingItem
                v-for="menu in recommendation.menus"
                :key="menu.id"
                :menu="menu"
                class="px-5"
              />
            </div>
          </div>
        </div>

        <!-- 피드백 섹션 -->
        <div class="bg-white rounded-xl p-6 shadow-sm max-w-2xl mx-auto">
          <div v-if="!feedbackGiven">
            <p class="text-base font-semibold text-gray-800 mb-4 text-center">이 추천이 도움이 됐나요?</p>
            <div class="flex gap-4">
              <Button variant="outline" class="flex-1 h-12 text-base" @click="handleFeedback('like')">
                👍 도움됐어요
              </Button>
              <Button variant="outline" class="flex-1 h-12 text-base" @click="handleFeedback('dislike')">
                👎 아쉬워요
              </Button>
            </div>
          </div>

          <div v-else>
            <p class="text-center text-base font-medium text-gray-700 mb-4">
              {{ feedbackGiven === 'like' ? '👍 피드백 감사합니다!' : '👎 소중한 의견 감사합니다!' }}
            </p>
            <div v-if="showReviewInput">
              <Textarea
                v-model="reviewText"
                placeholder="추가 의견을 남겨주시면 더 좋은 추천에 도움이 됩니다. (선택)"
                :rows="3"
                class="mb-4"
              />
              <div class="flex gap-3">
                <Button variant="outline" class="flex-1 h-11" @click="router.push('/home')">건너뛰기</Button>
                <Button class="flex-1 h-11" @click="submitReview">의견 남기기</Button>
              </div>
            </div>
          </div>
        </div>

        <!-- 하단 액션 -->
        <div class="flex justify-center mt-6">
          <Button variant="outline" class="h-11 px-8" @click="router.back()">
            ← 다른 와인으로 다시 추천
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
