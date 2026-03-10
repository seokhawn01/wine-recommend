<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTasteStore } from '@/stores/taste'
import { wines, mockUserProfile } from '@/mock/data'
import TasteRadarChart from '@/components/chart/TasteRadarChart.vue'
import WineCard from '@/components/wine/WineCard.vue'
import Button from '@/components/ui/button/Button.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

const router = useRouter()
const authStore = useAuthStore()
const tasteStore = useTasteStore()

// Mock 와인 컬렉션
const myWines = ref(wines.slice(0, 4))

const profile = authStore.user || mockUserProfile

// 취향 라벨 변환
function getTasteLabel(value, low, high) {
  if (value >= 4) return high
  if (value >= 2.5) return '보통'
  return low
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-8">마이페이지</h1>

      <!-- 메인 2열 레이아웃 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 왼쪽: 프로필 -->
        <div class="lg:col-span-1 space-y-6">
          <!-- 프로필 카드 -->
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <div class="flex items-center gap-4 mb-6">
              <Avatar class="w-16 h-16">
                <AvatarFallback class="text-2xl text-[#722F37] bg-[#FFF8F0]">
                  {{ profile.nickname?.charAt(0) || 'U' }}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 class="font-bold text-gray-900 text-lg">{{ profile.nickname }}</h2>
                <p class="text-sm text-gray-500">{{ profile.email }}</p>
                <div class="flex gap-2 mt-2">
                  <Badge variant="secondary" class="text-xs">와인 {{ myWines.length }}병</Badge>
                  <Badge variant="secondary" class="text-xs">리뷰 0개</Badge>
                </div>
              </div>
            </div>
            <Button
              variant="outline"
              class="w-full text-gray-500"
              @click="authStore.logout(); router.push('/login')"
            >
              로그아웃
            </Button>
          </div>

          <!-- 취향 프로파일 카드 -->
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-gray-800">🍷 내 와인 취향</h3>
              <router-link to="/onboarding" class="text-xs text-[#722F37] font-medium hover:underline">재설정 →</router-link>
            </div>

            <!-- 레이더 차트 -->
            <div class="flex justify-center mb-4">
              <TasteRadarChart
                :tannin="tasteStore.tannin"
                :acidity="tasteStore.acidity"
                :body="tasteStore.body"
                :sweetness="tasteStore.sweetness"
                size="lg"
              />
            </div>

            <!-- 수치 표시 -->
            <div class="grid grid-cols-2 gap-2.5">
              <div v-for="item in [
                { label: '타닌', value: tasteStore.tannin, low: '부드러움', high: '떫음' },
                { label: '산미', value: tasteStore.acidity, low: '묵직함', high: '상큼함' },
                { label: '바디감', value: tasteStore.body, low: '라이트', high: '풀바디' },
                { label: '당도', value: tasteStore.sweetness, low: '드라이', high: '스위트' },
              ]" :key="item.label"
                class="bg-gray-50 rounded-lg p-3"
              >
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs text-gray-600">{{ item.label }}</span>
                  <span class="text-xs font-bold text-[#722F37]">{{ item.value.toFixed(1) }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    class="h-1.5 bg-[#722F37] rounded-full"
                    :style="{ width: `${(item.value / 5) * 100}%` }"
                  />
                </div>
                <p class="text-xs text-gray-400 mt-1">{{ getTasteLabel(item.value, item.low, item.high) }}</p>
              </div>
            </div>
          </div>

          <!-- 선호 향 -->
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <h3 class="font-semibold text-gray-800 mb-3">🌸 선호 향</h3>
            <div v-if="tasteStore.preferredAromas.length" class="flex flex-wrap gap-2">
              <Badge v-for="a in tasteStore.preferredAromas" :key="a" variant="default" class="text-xs">
                {{ a }}
              </Badge>
            </div>
            <p v-else class="text-sm text-gray-400">
              설정된 선호 향이 없습니다.
              <router-link to="/onboarding" class="text-[#722F37]">설정하기</router-link>
            </p>
          </div>
        </div>

        <!-- 오른쪽: 와인 컬렉션 + 피드백 이력 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 와인 컬렉션 -->
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <div class="flex items-center justify-between mb-5">
              <h3 class="font-bold text-gray-800 text-lg">🍾 내 와인 컬렉션</h3>
              <Button size="sm" @click="router.push('/wine/register')">
                + 와인 추가
              </Button>
            </div>

            <div v-if="myWines.length" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
              <WineCard v-for="wine in myWines" :key="wine.id" :wine="wine" />
            </div>
            <div v-else class="py-16 text-center">
              <div class="text-4xl mb-3">🍾</div>
              <p class="text-gray-500 text-sm mb-4">아직 등록된 와인이 없습니다.</p>
              <Button @click="router.push('/wine/register')">첫 와인 등록하기</Button>
            </div>
          </div>

          <!-- 피드백 이력 -->
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <h3 class="font-bold text-gray-800 text-lg mb-4">📋 피드백 이력</h3>
            <div class="space-y-3">
              <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <span class="text-xl">👍</span>
                <div>
                  <p class="text-sm font-medium text-gray-800">티본스테이크 + 까베르네 소비뇽</p>
                  <p class="text-xs text-gray-400">데이트 · 2일 전</p>
                </div>
              </div>
              <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <span class="text-xl">👎</span>
                <div>
                  <p class="text-sm font-medium text-gray-800">해산물 파스타 + 샤르도네</p>
                  <p class="text-xs text-gray-400">친구 모임 · 1주 전</p>
                </div>
              </div>
              <p class="text-xs text-gray-400 text-center pt-2">피드백이 쌓일수록 AI 추천이 더 정확해집니다</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
