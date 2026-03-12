<script setup>
import { useRoute } from 'vue-router'
import { Home, Map, User } from 'lucide-vue-next'

const route = useRoute()

const navItems = [
  { label: '홈',      to: '/home',   icon: Home, matchPaths: ['/home', '/restaurant', '/match'] },
  { label: '지도',    to: '/map',    icon: Map,  matchPaths: ['/map'] },
  { label: '마이페이지', to: '/mypage', icon: User, matchPaths: ['/mypage', '/wine/register', '/ocr'] },
]

function isActive(item) {
  return item.matchPaths.some((p) => route.path.startsWith(p))
}
</script>

<template>
  <nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[390px] z-50 bg-white border-t border-gray-100 safe-area-bottom">
    <div class="flex items-center justify-around h-16">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex flex-col items-center gap-1 flex-1 py-2 transition-colors duration-150"
        :class="isActive(item) ? 'text-[#722F37]' : 'text-gray-400'"
      >
        <component :is="item.icon" :size="22" :stroke-width="isActive(item) ? 2.5 : 1.8" />
        <span class="text-[10px] font-medium">{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>
