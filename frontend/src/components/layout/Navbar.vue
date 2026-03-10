<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navItems = [
  { label: '홈', to: '/home', matchPaths: ['/home', '/restaurant'] },
  { label: 'AI 매칭', to: '/match', matchPaths: ['/match'] },
]

function isActive(item) {
  return item.matchPaths.some((p) => route.path.startsWith(p))
}
</script>

<template>
  <header class="sticky top-0 z-50 bg-white border-b border-gray-100 shadow-sm">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <!-- 로고 -->
      <router-link to="/home" class="flex items-center gap-2 shrink-0">
        <span class="text-2xl">🍷</span>
        <span class="font-bold text-[#722F37] text-xl tracking-tight">WinePair</span>
      </router-link>

      <!-- 중앙 네비게이션 -->
      <nav class="flex items-center gap-1">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="isActive(item)
            ? 'bg-[#722F37] text-white'
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'"
        >
          {{ item.label }}
        </router-link>
      </nav>

      <!-- 우측 사용자 메뉴 -->
      <div class="flex items-center gap-2 shrink-0">
        <template v-if="authStore.isLoggedIn">
          <router-link
            to="/mypage"
            class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="route.path.startsWith('/mypage') || route.path.startsWith('/wine')
              ? 'bg-[#722F37] text-white'
              : 'text-gray-600 hover:bg-gray-100'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            마이페이지
          </router-link>
          <button
            class="px-3 py-2 rounded-lg text-sm font-medium text-gray-500 hover:bg-gray-100 transition-colors"
            @click="authStore.logout(); router.push('/login')"
          >
            로그아웃
          </button>
        </template>
        <template v-else>
          <router-link
            to="/login"
            class="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
          >
            로그인
          </router-link>
          <router-link
            to="/signup"
            class="px-4 py-2 rounded-lg text-sm font-medium bg-[#722F37] text-white hover:bg-[#5a2129] transition-colors"
          >
            회원가입
          </router-link>
        </template>
      </div>
    </div>
  </header>
</template>
