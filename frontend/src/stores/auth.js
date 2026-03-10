import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/lib/supabaseClient'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)
  const isOnboardingDone = computed(() => user.value?.onboardingDone ?? false)

  // Supabase 사용자 객체를 앱 형식으로 변환
  function mapUser(supabaseUser) {
    return {
      id: supabaseUser.id,
      email: supabaseUser.email,
      nickname: supabaseUser.user_metadata?.nickname ?? supabaseUser.email.split('@')[0],
      onboardingDone: supabaseUser.user_metadata?.onboarding_done ?? false,
    }
  }

  // 앱 시작 시 기존 세션 복원 + 상태 변경 감지
  async function init() {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      user.value = mapUser(session.user)
    }
    supabase.auth.onAuthStateChange((_event, session) => {
      user.value = session?.user ? mapUser(session.user) : null
    })
  }

  async function login(email, password) {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error
      user.value = mapUser(data.user)
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  async function signup(email, password, nickname) {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { nickname, onboarding_done: false } },
      })
      if (error) throw error
      user.value = mapUser(data.user)
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    await supabase.auth.signOut()
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
    init,
    login,
    signup,
    logout,
    completeOnboarding,
  }
})
