<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTasteStore } from '@/stores/taste'
import { wines, mockUserProfile } from '@/mock/data'
import TasteNebulaChart from '@/components/chart/TasteNebulaChart.vue'
import WineCard from '@/components/wine/WineCard.vue'
import Button from '@/components/ui/button/Button.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Settings, Plus, ChevronRight, ThumbsUp, ThumbsDown } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const tasteStore = useTasteStore()

const myWines = ref(wines.slice(0, 4))
const profile = authStore.user || mockUserProfile

const tasteItems = [
  { label: '타닌', value: () => tasteStore.tannin, low: '부드러움', high: '떫음', color: 'bg-purple-500' },
  { label: '산미', value: () => tasteStore.acidity, low: '묵직함', high: '상큼함', color: 'bg-blue-500' },
  { label: '바디', value: () => tasteStore.body, low: '라이트', high: '풀바디', color: 'bg-rose-500' },
  { label: '당도', value: () => tasteStore.sweetness, low: '드라이', high: '스위트', color: 'bg-amber-500' },
]

const feedbacks = [
  { icon: ThumbsUp, text: '티본스테이크 + 까베르네 소비뇽', sub: '데이트 · 2일 전', positive: true },
  { icon: ThumbsDown, text: '해산물 파스타 + 샤르도네', sub: '친구 모임 · 1주 전', positive: false },
]
</script>

<template>
  <div class="min-h-screen bg-[#FFF8F0]">
    <!-- 헤더 -->
    <header class="flex items-center justify-between px-5 pt-12 pb-4">
      <h1 class="text-lg font-bold text-[#722F37]">마이페이지</h1>
      <button class="p-2" @click="router.push('/onboarding')">
        <Settings :size="20" class="text-gray-500" />
      </button>
    </header>

    <!-- 프로필 카드 -->
    <section class="mx-5 bg-white rounded-2xl p-5 shadow-sm mb-4">
      <div class="flex items-center gap-4">
        <Avatar class="w-14 h-14">
          <AvatarFallback class="text-xl text-[#722F37] bg-[#FFF8F0]">
            {{ profile.nickname?.charAt(0) || 'U' }}
          </AvatarFallback>
        </Avatar>
        <div class="flex-1">
          <h2 class="font-bold text-gray-900">{{ profile.nickname }}</h2>
          <p class="text-xs text-gray-400">{{ profile.email }}</p>
          <div class="flex gap-2 mt-1.5">
            <Badge variant="secondary" class="text-xs">와인 {{ myWines.length }}병</Badge>
            <Badge variant="secondary" class="text-xs">리뷰 0개</Badge>
          </div>
        </div>
        <button
          class="text-xs text-gray-400 border border-gray-200 px-2.5 py-1.5 rounded-lg"
          @click="authStore.logout(); router.push('/login')"
        >
          로그아웃
        </button>
      </div>
    </section>

    <!-- 취향 성운 -->
    <section class="mx-5 bg-white rounded-2xl p-5 shadow-sm mb-4">
      <div class="flex items-center justify-between mb-1">
        <h3 class="text-sm font-bold text-gray-800">🍷 내 와인 취향 성운</h3>
        <button class="text-xs text-[#722F37]" @click="router.push('/onboarding')">
          재설정 →
        </button>
      </div>

      <!-- 성운 시각화 -->
      <div class="flex justify-center my-2">
        <TasteNebulaChart
          :tannin="tasteStore.tannin"
          :acidity="tasteStore.acidity"
          :body="tasteStore.body"
          :sweetness="tasteStore.sweetness"
          :size="220"
        />
      </div>

      <!-- 바 형태 수치 -->
      <div class="grid grid-cols-2 gap-2.5 mt-1">
        <div
          v-for="item in tasteItems"
          :key="item.label"
          class="bg-gray-50 rounded-xl p-3"
        >
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs text-gray-600">{{ item.label }}</span>
            <span class="text-xs font-bold text-[#722F37]">{{ item.value().toFixed(1) }}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-1.5">
            <div
              :class="['h-1.5 rounded-full', item.color]"
              :style="{ width: `${(item.value() / 5) * 100}%` }"
            />
          </div>
        </div>
      </div>

      <!-- 선호 향 -->
      <div v-if="tasteStore.preferredAromas.length" class="mt-4 flex flex-wrap gap-1.5">
        <Badge v-for="a in tasteStore.preferredAromas" :key="a" variant="default" class="text-xs">
          {{ a }}
        </Badge>
      </div>
    </section>

    <!-- 내 와인 컬렉션 -->
    <section class="mx-5 bg-white rounded-2xl p-5 shadow-sm mb-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-bold text-gray-800">🍾 내 와인 컬렉션</h3>
        <button
          class="flex items-center gap-1 text-xs text-[#722F37] bg-[#FFF8F0] px-2.5 py-1.5 rounded-lg font-medium"
          @click="router.push('/ocr')"
        >
          <Plus :size="13" /> 추가
        </button>
      </div>

      <div v-if="myWines.length" class="grid grid-cols-2 gap-3">
        <WineCard v-for="wine in myWines" :key="wine.id" :wine="wine" />
      </div>
      <div v-else class="py-10 text-center">
        <p class="text-3xl mb-2">🍾</p>
        <p class="text-sm text-gray-400 mb-3">아직 등록된 와인이 없어요</p>
        <Button size="sm" @click="router.push('/ocr')">첫 와인 등록</Button>
      </div>
    </section>

    <!-- 피드백 이력 -->
    <section class="mx-5 bg-white rounded-2xl p-5 shadow-sm mb-4">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-bold text-gray-800">📋 피드백 이력</h3>
        <button class="flex items-center gap-0.5 text-xs text-[#722F37]">
          전체 보기 <ChevronRight :size="13" />
        </button>
      </div>

      <div class="space-y-2.5">
        <div
          v-for="fb in feedbacks"
          :key="fb.text"
          class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl"
        >
          <div :class="['w-8 h-8 rounded-full flex items-center justify-center shrink-0', fb.positive ? 'bg-green-100' : 'bg-red-100']">
            <component :is="fb.icon" :size="14" :class="fb.positive ? 'text-green-600' : 'text-red-500'" />
          </div>
          <div>
            <p class="text-xs font-medium text-gray-800">{{ fb.text }}</p>
            <p class="text-[10px] text-gray-400 mt-0.5">{{ fb.sub }}</p>
          </div>
        </div>
      </div>
      <p class="text-[10px] text-gray-400 text-center mt-3">
        피드백이 쌓일수록 AI 추천이 더 정확해져요 ✨
      </p>
    </section>
  </div>
</template>
