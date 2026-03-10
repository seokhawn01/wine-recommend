<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Input from '@/components/ui/input/Input.vue'
import Button from '@/components/ui/button/Button.vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  if (!email.value || !password.value) {
    error.value = '이메일과 비밀번호를 입력해주세요.'
    return
  }
  error.value = ''
  const result = await authStore.login(email.value, password.value)
  if (result.success) {
    if (authStore.isOnboardingDone) {
      router.push('/home')
    } else {
      router.push('/onboarding')
    }
  }
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- 왼쪽: 브랜드 영역 -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#722F37] to-[#4a1c22] flex-col items-center justify-center p-12">
      <div class="text-center text-white max-w-md">
        <div class="text-8xl mb-6">🍷</div>
        <h1 class="text-5xl font-bold tracking-tight mb-4">WinePair</h1>
        <p class="text-xl text-white/80 mb-8">AI 소믈리에와 함께하는<br>완벽한 와인 × 메뉴 페어링</p>
        <div class="space-y-3 text-left">
          <div class="flex items-center gap-3 text-white/90">
            <span class="text-2xl">✓</span>
            <span>내 와인 × 식당 메뉴 매칭</span>
          </div>
          <div class="flex items-center gap-3 text-white/90">
            <span class="text-2xl">✓</span>
            <span>상황별 맞춤 소믈리에 추천</span>
          </div>
          <div class="flex items-center gap-3 text-white/90">
            <span class="text-2xl">✓</span>
            <span>피드백으로 진화하는 취향 학습</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 오른쪽: 로그인 폼 -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
      <div class="w-full max-w-md">
        <!-- 모바일용 로고 -->
        <div class="lg:hidden text-center mb-8">
          <div class="text-5xl mb-2">🍷</div>
          <h1 class="text-3xl font-bold text-[#722F37]">WinePair</h1>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 mb-2">로그인</h2>
        <p class="text-gray-500 mb-8">계정에 로그인하여 시작하세요.</p>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">이메일</label>
            <Input
              v-model="email"
              type="email"
              placeholder="이메일을 입력하세요"
              class="h-11"
              @keyup.enter="handleLogin"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">비밀번호</label>
            <Input
              v-model="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              class="h-11"
              @keyup.enter="handleLogin"
            />
          </div>

          <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

          <Button
            class="w-full h-11 text-base"
            :disabled="authStore.loading"
            @click="handleLogin"
          >
            {{ authStore.loading ? '로그인 중...' : '로그인' }}
          </Button>
        </div>

        <div class="flex items-center gap-3 my-6">
          <div class="flex-1 h-px bg-gray-200" />
          <span class="text-xs text-gray-400">또는</span>
          <div class="flex-1 h-px bg-gray-200" />
        </div>

        <p class="text-center text-sm text-gray-600">
          아직 계정이 없으신가요?
          <router-link to="/signup" class="text-[#722F37] font-semibold ml-1">회원가입</router-link>
        </p>
        <button
          class="w-full mt-3 text-sm text-gray-400 hover:text-gray-600 py-2 transition-colors"
          @click="router.push('/home')"
        >
          게스트로 둘러보기 →
        </button>
      </div>
    </div>
  </div>
</template>
