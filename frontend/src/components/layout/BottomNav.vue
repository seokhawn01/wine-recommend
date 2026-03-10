<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()

const navItems = [
  {
    label: '홈',
    to: '/home',
    matchPaths: ['/home', '/restaurant'],
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>`,
  },
  {
    label: 'AI 추천',
    to: '/match',
    matchPaths: ['/match'],
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>`,
  },
  {
    label: '마이',
    to: '/mypage',
    matchPaths: ['/mypage', '/wine/register'],
    icon: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>`,
  },
]

function isActive(item) {
  return item.matchPaths.some((p) => route.path.startsWith(p))
}
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-100 pb-safe">
    <div class="max-w-[390px] mx-auto flex items-center justify-around h-16">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex flex-col items-center gap-0.5 flex-1 py-2 transition-colors"
        :class="isActive(item) ? 'text-[#722F37]' : 'text-gray-400 hover:text-gray-600'"
      >
        <!-- eslint-disable vue/no-v-html -->
        <span v-html="item.icon" />
        <span class="text-xs font-medium">{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>
