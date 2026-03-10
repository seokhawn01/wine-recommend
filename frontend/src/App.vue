<script setup>
import { RouterView, useRoute } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'

const route = useRoute()

// 인증/온보딩 페이지는 Navbar 숨김
const hideNavbar = ['/login', '/signup', '/onboarding']
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar v-if="!hideNavbar.includes(route.path)" />
    <RouterView />
  </div>
</template>
