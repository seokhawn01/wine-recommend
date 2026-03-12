<script setup>
import { RouterView, useRoute } from 'vue-router'
import BottomNav from '@/components/layout/BottomNav.vue'

const route = useRoute()

// 인증/온보딩 페이지는 BottomNav 숨김
const hideNav = ['/login', '/signup', '/onboarding']
</script>

<template>
  <!-- 모바일 웹앱: 전체 화면을 크림색 배경으로, max-w-[390px] 중앙 정렬 -->
  <div class="min-h-screen bg-gray-100 flex justify-center">
    <div class="relative w-full max-w-[390px] min-h-screen bg-[#FFF8F0] flex flex-col shadow-xl">
      <RouterView class="flex-1" :class="{ 'pb-20': !hideNav.includes(route.path) }" />
      <BottomNav v-if="!hideNav.includes(route.path)" />
    </div>
  </div>
</template>
