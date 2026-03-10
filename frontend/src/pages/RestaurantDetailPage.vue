<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { restaurants, menus, wines, situations } from '@/mock/data'
import MenuPairingItem from '@/components/restaurant/MenuPairingItem.vue'
import Button from '@/components/ui/button/Button.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Select from '@/components/ui/select/Select.vue'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

const route = useRoute()
const router = useRouter()

const restaurantId = parseInt(route.params.id)
const restaurant = restaurants.find((r) => r.id === restaurantId)
const restaurantMenus = menus.filter((m) => m.restaurantId === restaurantId)

const selectedWineId = ref('')
const selectedSituation = ref('')

// 와인 선택 시 메뉴 페어링 점수 정렬 (선택한 와인과의 궁합 반영 — Mock이라 그대로)
const sortedMenus = computed(() => {
  return [...restaurantMenus].sort((a, b) => b.pairingScore - a.pairingScore)
})

function goToMatch() {
  if (!selectedWineId.value) return
  router.push({
    path: '/match',
    query: {
      restaurantId,
      wineId: selectedWineId.value,
      situation: selectedSituation.value,
    },
  })
}
</script>

<template>
  <div v-if="restaurant" class="min-h-screen bg-gray-50">
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
          홈으로
        </button>
        <span class="text-gray-300">/</span>
        <span class="text-sm text-gray-800 font-medium">{{ restaurant.name }}</span>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- 상단 식당 배너 -->
      <div class="bg-gradient-to-r from-[#722F37] to-[#9b4a52] rounded-2xl overflow-hidden mb-8">
        <div class="flex flex-col lg:flex-row">
          <!-- 이미지 영역 -->
          <div class="lg:w-80 h-48 lg:h-auto bg-gradient-to-br from-[#FFF8F0] to-[#F5E8D8] flex items-center justify-center shrink-0">
            <span class="text-8xl">🍽️</span>
          </div>
          <!-- 식당 정보 -->
          <div class="flex-1 p-6 text-white">
            <div class="flex items-start justify-between mb-3">
              <div>
                <h1 class="text-2xl font-bold mb-1">{{ restaurant.name }}</h1>
                <p class="text-white/80">{{ restaurant.address }}</p>
              </div>
              <div class="text-right">
                <div class="flex items-center gap-1 justify-end">
                  <span class="text-yellow-300 text-lg">★</span>
                  <span class="font-bold text-xl">{{ restaurant.rating }}</span>
                </div>
                <p class="text-white/60 text-sm">리뷰 {{ restaurant.feedbackCount }}개</p>
              </div>
            </div>

            <!-- 배지들 -->
            <div class="flex gap-2 flex-wrap mb-4">
              <span class="bg-white/20 text-white text-xs px-3 py-1.5 rounded-full font-medium">{{ restaurant.category }}</span>
              <span v-if="restaurant.corkageFee === 0" class="bg-yellow-400/90 text-yellow-900 text-xs px-3 py-1.5 rounded-full font-medium">🍾 콜키지 무료</span>
              <span v-else class="bg-white/20 text-white text-xs px-3 py-1.5 rounded-full font-medium">🍾 콜키지 {{ restaurant.corkageFee.toLocaleString() }}원</span>
              <span class="bg-white/20 text-white text-xs px-3 py-1.5 rounded-full font-medium">최대 {{ restaurant.corkageLimit }}병</span>
              <span v-if="restaurant.reservationRequired" class="bg-white/20 text-white text-xs px-3 py-1.5 rounded-full font-medium">📅 예약 필수</span>
            </div>

            <div class="flex gap-6 text-sm text-white/80">
              <span>📞 {{ restaurant.phone || '정보 없음' }}</span>
              <span>🕐 11:00 – 22:00</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 메인 컨텐츠: 2열 레이아웃 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 왼쪽: 페어링 설정 -->
        <div class="lg:col-span-1 space-y-4">
          <!-- 와인 & 상황 선택 -->
          <div class="bg-white rounded-xl p-6 shadow-sm sticky top-24">
            <h3 class="font-bold text-gray-800 text-lg mb-4">🍷 페어링 설정</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1.5">가져갈 와인 선택</label>
                <Select v-model="selectedWineId" placeholder="와인을 선택하세요">
                  <option v-for="wine in wines" :key="wine.id" :value="wine.id">
                    {{ wine.name }} ({{ wine.vintage || 'NV' }})
                  </option>
                </Select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1.5">방문 상황</label>
                <Select v-model="selectedSituation" placeholder="상황을 선택하세요">
                  <option v-for="s in situations" :key="s.value" :value="s.value">{{ s.label }}</option>
                </Select>
              </div>
              <Button
                class="w-full h-12 text-base"
                :disabled="!selectedWineId"
                @click="goToMatch"
              >
                AI 페어링 추천 받기 ✨
              </Button>
              <p v-if="!selectedWineId" class="text-xs text-gray-400 text-center">
                와인을 선택해야 추천을 받을 수 있어요
              </p>
            </div>

            <!-- 선택 와인 프리뷰 -->
            <div v-if="selectedWineId" class="mt-4 p-3 bg-[#FFF8F0] rounded-lg border border-[#722F37]/10">
              <p class="text-xs font-medium text-[#722F37] mb-1">선택된 와인</p>
              <p class="text-sm font-semibold text-gray-900">
                {{ wines.find(w => w.id == selectedWineId)?.name }}
              </p>
            </div>
          </div>
        </div>

        <!-- 오른쪽: 메뉴 -->
        <div class="lg:col-span-2">
          <Tabs default-value="pairing">
            <TabsList class="mb-4">
              <TabsTrigger value="pairing">🍷 와인 페어링</TabsTrigger>
              <TabsTrigger value="menu">📋 전체 메뉴</TabsTrigger>
            </TabsList>

            <!-- 와인 페어링 탭 -->
            <TabsContent value="pairing">
              <div class="bg-white rounded-xl shadow-sm overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-50">
                  <h3 class="font-semibold text-gray-800">
                    메뉴별 페어링 점수
                    <span v-if="selectedWineId" class="text-sm text-gray-400 font-normal ml-2">(선택 와인 기준)</span>
                    <span v-else class="text-sm text-gray-400 font-normal ml-2">(와인 선택 전 — 기본 순위)</span>
                  </h3>
                </div>
                <div class="divide-y divide-gray-50">
                  <MenuPairingItem
                    v-for="menu in sortedMenus"
                    :key="menu.id"
                    :menu="menu"
                    class="px-6"
                  />
                </div>
              </div>
            </TabsContent>

            <!-- 전체 메뉴 탭 -->
            <TabsContent value="menu">
              <div class="bg-white rounded-xl shadow-sm overflow-hidden">
                <div class="divide-y divide-gray-50">
                  <div v-for="menu in restaurantMenus" :key="menu.id"
                    class="px-6 py-4 hover:bg-gray-50 transition-colors">
                    <div class="flex justify-between items-start">
                      <div class="flex-1">
                        <div class="font-medium text-gray-900">{{ menu.name }}</div>
                        <div class="text-sm text-gray-500 mt-1">{{ menu.description }}</div>
                        <Badge variant="secondary" class="text-xs mt-2">{{ menu.category }}</Badge>
                      </div>
                      <span class="text-base font-semibold text-gray-800 shrink-0 ml-4">
                        {{ menu.price.toLocaleString() }}원
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  </div>

  <!-- 404 -->
  <div v-else class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="text-4xl mb-3">🔍</div>
      <p class="text-gray-500">식당을 찾을 수 없습니다.</p>
      <button class="mt-4 text-[#722F37] font-medium hover:underline" @click="router.push('/home')">홈으로 돌아가기</button>
    </div>
  </div>
</template>
