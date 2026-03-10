<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Input from '@/components/ui/input/Input.vue'
import Button from '@/components/ui/button/Button.vue'

const router = useRouter()
const authStore = useAuthStore()

const nickname = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const error = ref('')

async function handleSignup() {
  if (!nickname.value || !email.value || !password.value) {
    error.value = '모든 항목을 입력해주세요.'
    return
  }
  if (password.value !== passwordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  if (password.value.length < 6) {
    error.value = '비밀번호는 6자 이상이어야 합니다.'
    return
  }
  error.value = ''
  const result = await authStore.signup(email.value, password.value, nickname.value)
  if (result.success) {
    router.push('/onboarding')
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
        <p class="text-xl text-white/80 mb-8">나만의 취향으로<br>완벽한 페어링 시작하기</p>
        <div class="space-y-3 text-left">
          <div class="flex items-center gap-3 text-white/90">
            <span class="text-2xl">✓</span>
            <span>콜키지 식당 근처 탐색</span>
          </div>
          <div class="flex items-center gap-3 text-white/90">
            <span class="text-2xl">✓</span>
            <span>와인 취향 프로파일 설정</span>
          </div>
          <div class="flex items-center gap-3 text-white/90">
            <span class="text-2xl">✓</span>
            <span>AI 소믈리에 메뉴 추천</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 오른쪽: 회원가입 폼 -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
      <div class="w-full max-w-md">
        <!-- 모바일용 로고 -->
        <div class="lg:hidden text-center mb-8">
          <div class="text-5xl mb-2">🍷</div>
          <h1 class="text-3xl font-bold text-[#722F37]">WinePair</h1>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 mb-2">회원가입</h2>
        <p class="text-gray-500 mb-8">계정을 만들어 시작해보세요.</p>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">닉네임</label>
            <Input v-model="nickname" placeholder="닉네임을 입력하세요" class="h-11" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">이메일</label>
            <Input v-model="email" type="email" placeholder="이메일을 입력하세요" class="h-11" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">비밀번호</label>
            <Input v-model="password" type="password" placeholder="비밀번호 (6자 이상)" class="h-11" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">비밀번호 확인</label>
            <Input
              v-model="passwordConfirm"
              type="password"
              placeholder="비밀번호를 다시 입력하세요"
              class="h-11"
              @keyup.enter="handleSignup"
            />
          </div>

          <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

          <Button
            class="w-full h-11 text-base"
            :disabled="authStore.loading"
            @click="handleSignup"
          >
            {{ authStore.loading ? '처리 중...' : '회원가입' }}
          </Button>
        </div>

        <p class="text-center text-sm text-gray-600 mt-6">
          이미 계정이 있으신가요?
          <router-link to="/login" class="text-[#722F37] font-semibold ml-1">로그인</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
