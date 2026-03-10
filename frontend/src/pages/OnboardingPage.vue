<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTasteStore } from '@/stores/taste'
import { useAuthStore } from '@/stores/auth'
import { aromas, dietaryRestrictions } from '@/mock/data'
import Slider from '@/components/ui/slider/Slider.vue'
import Button from '@/components/ui/button/Button.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import TasteRadarChart from '@/components/chart/TasteRadarChart.vue'

const router = useRouter()
const tasteStore = useTasteStore()
const authStore = useAuthStore()

const step = ref(1) // 1: 맛 프로파일, 2: 취향 선택

const sliders = [
  { key: 'tannin', label: '타닌', desc: '낮음 (부드러움) ↔ 높음 (떫음)', emoji: '🍇' },
  { key: 'acidity', label: '산미', desc: '낮음 (묵직함) ↔ 높음 (상큼함)', emoji: '🍋' },
  { key: 'body', label: '바디감', desc: '가벼움 (라이트) ↔ 무거움 (풀바디)', emoji: '⚖️' },
  { key: 'sweetness', label: '당도', desc: '드라이 ↔ 스위트', emoji: '🍯' },
]

function handleComplete() {
  tasteStore.setTasteProfile({
    tannin: tasteStore.tannin,
    acidity: tasteStore.acidity,
    body: tasteStore.body,
    sweetness: tasteStore.sweetness,
    preferredAromas: tasteStore.preferredAromas,
    dietaryRestrictions: tasteStore.dietaryRestrictions,
  })
  authStore.completeOnboarding()
  router.push('/home')
}
</script>

<template>
  <div class="min-h-screen bg-[#FFF8F0]">
    <!-- 상단 진행 표시 헤더 -->
    <div class="bg-white border-b border-gray-100 px-6 py-4">
      <div class="max-w-4xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🍷</span>
          <span class="font-bold text-[#722F37] text-lg">WinePair</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500">취향 설정</span>
          <div class="flex gap-1.5">
            <div
              v-for="i in 2"
              :key="i"
              class="h-1.5 rounded-full transition-all"
              :class="[i <= step ? 'bg-[#722F37] w-8' : 'bg-gray-200 w-4']"
            />
          </div>
          <span class="text-sm text-gray-400">{{ step }}/2</span>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-6 py-10">
      <!-- Step 1: 맛 프로파일 -->
      <div v-if="step === 1">
        <div class="mb-8 text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">어떤 와인을 좋아하세요?</h1>
          <p class="text-gray-500">슬라이더를 조정해 와인 취향을 설정해주세요. 나중에 언제든 변경할 수 있습니다.</p>
        </div>

        <!-- 2열 레이아웃: 차트 | 슬라이더 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 레이더 차트 -->
          <div class="bg-white rounded-2xl p-8 shadow-sm flex flex-col items-center justify-center">
            <h2 class="font-semibold text-gray-700 mb-6 text-center">내 취향 레이더</h2>
            <TasteRadarChart
              :tannin="tasteStore.tannin"
              :acidity="tasteStore.acidity"
              :body="tasteStore.body"
              :sweetness="tasteStore.sweetness"
              size="lg"
            />
            <p class="text-sm text-gray-400 mt-4 text-center">슬라이더를 조작하면 실시간으로 반영됩니다</p>
          </div>

          <!-- 슬라이더 -->
          <div class="bg-white rounded-2xl p-8 shadow-sm">
            <h2 class="font-semibold text-gray-700 mb-6">맛 프로파일 설정</h2>
            <div class="space-y-6">
              <div v-for="item in sliders" :key="item.key">
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center gap-2">
                    <span class="text-xl">{{ item.emoji }}</span>
                    <span class="font-medium text-gray-900">{{ item.label }}</span>
                  </div>
                  <span class="text-lg font-bold text-[#722F37]">{{ tasteStore[item.key].toFixed(1) }}</span>
                </div>
                <Slider
                  :model-value="tasteStore[item.key]"
                  :min="0"
                  :max="5"
                  :step="0.1"
                  @update:model-value="tasteStore[item.key] = $event"
                />
                <div class="flex justify-between text-xs text-gray-400 mt-1.5">
                  <span>{{ item.desc.split('↔')[0].trim() }}</span>
                  <span>{{ item.desc.split('↔')[1]?.trim() }}</span>
                </div>
              </div>
            </div>

            <Button class="w-full h-12 mt-8 text-base" @click="step = 2">
              다음: 향 & 식이 제한 설정 →
            </Button>
          </div>
        </div>
      </div>

      <!-- Step 2: 향 & 식이제한 -->
      <div v-else>
        <div class="mb-8 text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">선호 향과 식이 제한을 설정하세요</h1>
          <p class="text-gray-500">여러 개 선택 가능합니다. 건너뛰어도 괜찮아요.</p>
        </div>

        <!-- 2열 레이아웃 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 선호 향 -->
          <div class="bg-white rounded-2xl p-8 shadow-sm">
            <h2 class="font-semibold text-gray-800 mb-4 text-lg">🌸 선호하는 향</h2>
            <p class="text-sm text-gray-500 mb-4">와인에서 즐기는 향을 선택해주세요.</p>
            <div class="flex flex-wrap gap-2">
              <Badge
                v-for="aroma in aromas"
                :key="aroma"
                :variant="tasteStore.preferredAromas.includes(aroma) ? 'selected' : 'unselected'"
                class="cursor-pointer text-sm py-1.5 px-3 border-0"
                @click="tasteStore.toggleAroma(aroma)"
              >
                {{ aroma }}
              </Badge>
            </div>
          </div>

          <!-- 식이제한 -->
          <div class="bg-white rounded-2xl p-8 shadow-sm">
            <h2 class="font-semibold text-gray-800 mb-4 text-lg">🚫 식이 제한</h2>
            <p class="text-sm text-gray-500 mb-4">못 드시는 음식이 있으면 선택해주세요. 메뉴 추천 시 자동으로 제외됩니다.</p>
            <div class="flex flex-wrap gap-2">
              <Badge
                v-for="r in dietaryRestrictions"
                :key="r"
                :variant="tasteStore.dietaryRestrictions.includes(r) ? 'selected' : 'unselected'"
                class="cursor-pointer text-sm py-1.5 px-3 border-0"
                @click="tasteStore.toggleRestriction(r)"
              >
                {{ r }}
              </Badge>
            </div>

            <div class="flex gap-3 mt-8">
              <Button variant="outline" class="flex-1 h-12" @click="step = 1">← 이전</Button>
              <Button class="flex-1 h-12 text-base" @click="handleComplete">시작하기 🎉</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
