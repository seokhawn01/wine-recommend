import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { mockUserProfile } from '@/mock/data'

export const useAuthStore = defineStore('auth', () => {
  // Mock 상태 — 백엔드 API 연동 후 Supabase Auth로 교체
  const user = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)
  const isOnboardingDone = computed(() => user.value?.onboardingDone ?? false)

  function login(email, password) {
    loading.value = true
    // Mock 로그인
    return new Promise((resolve) => {
      setTimeout(() => {
        user.value = { ...mockUserProfile, email }
        loading.value = false
        resolve({ success: true })
      }, 800)
    })
  }

  function signup(email, password, nickname) {
    loading.value = true
    return new Promise((resolve) => {
      setTimeout(() => {
        user.value = {
          ...mockUserProfile,
          email,
          nickname,
          onboardingDone: false,
        }
        loading.value = false
        resolve({ success: true })
      }, 800)
    })
  }

  function logout() {
    user.value = null
  }

  function completeOnboarding() {
    if (user.value) {
      user.value.onboardingDone = true
    }
  }

  return {
    user,
    loading,
    isLoggedIn,
    isOnboardingDone,
    login,
    signup,
    logout,
    completeOnboarding,
  }
})
