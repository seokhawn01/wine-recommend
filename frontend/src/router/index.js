import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/pages/auth/LoginPage.vue'
import SignupPage from '@/pages/auth/SignupPage.vue'
import OnboardingPage from '@/pages/OnboardingPage.vue'
import HomePage from '@/pages/HomePage.vue'
import RestaurantDetailPage from '@/pages/RestaurantDetailPage.vue'
import AiMatchPage from '@/pages/AiMatchPage.vue'
import MyPage from '@/pages/MyPage.vue'
import WineRegisterPage from '@/pages/WineRegisterPage.vue'
import MapPage from '@/pages/MapPage.vue'
import OcrPage from '@/pages/OcrPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/home' },
    { path: '/login', component: LoginPage },
    { path: '/signup', component: SignupPage },
    { path: '/onboarding', component: OnboardingPage },
    { path: '/home', component: HomePage },
    { path: '/map', component: MapPage },
    { path: '/restaurant/:id', component: RestaurantDetailPage },
    { path: '/match', component: AiMatchPage },
    { path: '/mypage', component: MyPage },
    { path: '/ocr', component: OcrPage },
    { path: '/wine/register', component: WineRegisterPage },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
