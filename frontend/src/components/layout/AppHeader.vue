<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

defineProps({
  title: { type: String, default: '' },
  showBack: { type: Boolean, default: false },
})
</script>

<template>
  <header class="sticky top-0 z-50 bg-white border-b border-gray-100 px-4 h-14 flex items-center justify-between">
    <!-- 왼쪽: 뒤로가기 또는 로고 -->
    <div class="flex items-center gap-2">
      <button v-if="showBack" @click="router.back()" class="p-1 -ml-1 hover:bg-gray-100 rounded-full">
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <router-link v-else to="/home" class="flex items-center gap-1.5">
        <span class="text-2xl">🍷</span>
        <span class="font-bold text-[#722F37] text-lg tracking-tight">WinePair</span>
      </router-link>
    </div>

    <!-- 가운데: 타이틀 -->
    <h1 v-if="title" class="font-semibold text-gray-800 text-base absolute left-1/2 -translate-x-1/2">
      {{ title }}
    </h1>

    <!-- 오른쪽: 액션 버튼 -->
    <div class="flex items-center gap-1">
      <slot name="actions">
        <router-link v-if="authStore.isLoggedIn" to="/mypage" class="p-1 hover:bg-gray-100 rounded-full">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </router-link>
        <router-link v-else to="/login" class="p-1 hover:bg-gray-100 rounded-full">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
          </svg>
        </router-link>
      </slot>
    </div>
  </header>
</template>
