<script setup>
/**
 * OcrPage.vue — 와인 라벨 촬영 전용 (모바일)
 * GPT Vision(gpt-4o-mini)으로 라벨 이미지 → 와인 정보 자동 추출
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/components/ui/button/Button.vue'
import Slider from '@/components/ui/slider/Slider.vue'
import { Camera, X, Check, RotateCcw, AlertCircle } from 'lucide-vue-next'
import { useWineVision } from '@/composables/useWineVision'

const router = useRouter()
const { analyzeWineLabel, isLoading: isOcrLoading, error: visionError } = useWineVision()

const previewImage = ref(null)
const isSubmitting = ref(false)
const step = ref('capture') // 'capture' | 'edit' | 'done'

const form = ref({
  name: '',
  grape: '',
  region: '',
  vintage: '',
  type: 'red',
  tannin: 2.5,
  acidity: 2.5,
  body: 2.5,
  sweetness: 2.5,
})

const wineTypes = [
  { value: 'red', label: '레드', emoji: '🍷' },
  { value: 'white', label: '화이트', emoji: '🥂' },
  { value: 'sparkling', label: '스파클링', emoji: '🍾' },
  { value: 'rose', label: '로제', emoji: '🌸' },
]

const tasteSliders = [
  { key: 'tannin', label: '타닌', emoji: '🍇' },
  { key: 'acidity', label: '산미', emoji: '🍋' },
  { key: 'body', label: '바디감', emoji: '⚖️' },
  { key: 'sweetness', label: '당도', emoji: '🍯' },
]

function handleImageUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    previewImage.value = ev.target.result
    runVisionOcr(ev.target.result)
  }
  reader.readAsDataURL(file)
}

async function runVisionOcr(imageDataUrl) {
  step.value = 'capture'
  const result = await analyzeWineLabel(imageDataUrl)

  if (!result) {
    // 에러는 visionError에 이미 담겨 있음
    step.value = 'capture'
    return
  }

  // GPT 응답을 form에 적용
  form.value.name = result.name
  form.value.grape = result.grape
  form.value.region = result.region
  form.value.vintage = result.vintage
  form.value.type = result.type
  form.value.tannin = result.tannin
  form.value.acidity = result.acidity
  form.value.body = result.body
  form.value.sweetness = result.sweetness
  step.value = 'edit'
}

function handleReset() {
  previewImage.value = null
  form.value = { name: '', grape: '', region: '', vintage: '', type: 'red', tannin: 2.5, acidity: 2.5, body: 2.5, sweetness: 2.5 }
  step.value = 'capture'
}

function handleSubmit() {
  if (!form.value.name) return
  isSubmitting.value = true
  setTimeout(() => {
    isSubmitting.value = false
    step.value = 'done'
  }, 800)
}
</script>

<template>
  <div class="flex flex-col min-h-screen bg-[#FFF8F0]">
    <!-- 헤더 -->
    <header class="flex items-center justify-between px-5 pt-12 pb-4">
      <div>
        <h1 class="text-lg font-bold text-[#722F37]">📷 와인 라벨 촬영</h1>
        <p class="text-xs text-gray-400 mt-0.5">라벨을 찍으면 정보를 자동으로 인식해요</p>
      </div>
      <button class="p-2" @click="router.back()">
        <X :size="20" class="text-gray-500" />
      </button>
    </header>

    <!-- 완료 화면 -->
    <div v-if="step === 'done'" class="flex-1 flex flex-col items-center justify-center px-5 pb-20">
      <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-4">
        <Check :size="36" class="text-green-600" />
      </div>
      <h2 class="text-lg font-bold text-gray-900 mb-1">와인이 등록되었습니다!</h2>
      <p class="text-sm text-gray-500 text-center mb-8">{{ form.name }}이(가) 컬렉션에 추가되었어요.</p>
      <Button class="w-full h-12" @click="router.push('/mypage')">컬렉션 보러 가기</Button>
      <button class="mt-3 text-sm text-gray-500" @click="handleReset">다른 와인 추가</button>
    </div>

    <!-- 촬영/인식 화면 -->
    <div v-else class="flex-1 flex flex-col px-5 pb-6 gap-4">
      <!-- 이미지 업로드 영역 -->
      <div class="flex-shrink-0">
        <label class="block cursor-pointer">
          <div
            v-if="!previewImage"
            class="border-2 border-dashed border-[#722F37]/30 rounded-2xl h-52 flex flex-col items-center justify-center bg-white active:bg-[#FFF8F0] transition"
          >
            <Camera :size="40" class="text-[#722F37]/50 mb-3" />
            <p class="text-sm font-semibold text-gray-700">와인 라벨 촬영 / 갤러리</p>
            <p class="text-xs text-gray-400 mt-1">JPG, PNG · 최대 10MB</p>
          </div>
          <div v-else class="relative rounded-2xl overflow-hidden h-52 bg-gray-100">
            <img :src="previewImage" class="w-full h-full object-contain" alt="와인 라벨" />
            <div
              v-if="isOcrLoading"
              class="absolute inset-0 bg-black/40 flex flex-col items-center justify-center"
            >
              <div class="w-8 h-8 border-3 border-white border-t-transparent rounded-full animate-spin mb-2" />
              <p class="text-white text-sm font-medium">GPT Vision 분석 중...</p>
            </div>
          </div>
          <input type="file" accept="image/*" capture="environment" class="hidden" @change="handleImageUpload" />
        </label>

        <!-- 다시 촬영 버튼 -->
        <button v-if="previewImage && !isOcrLoading" class="flex items-center gap-1.5 text-xs text-gray-500 mt-2 mx-auto" @click="handleReset">
          <RotateCcw :size="12" /> 다시 촬영
        </button>

        <!-- Vision API 에러 표시 -->
        <div v-if="visionError" class="mt-3 flex items-start gap-2 p-3 bg-red-50 rounded-xl border border-red-200">
          <AlertCircle :size="16" class="text-red-500 shrink-0 mt-0.5" />
          <div>
            <p class="text-xs font-semibold text-red-700">라벨 인식 실패</p>
            <p class="text-xs text-red-600 mt-0.5">{{ visionError }}</p>
          </div>
        </div>
      </div>

      <!-- OCR 결과 편집 -->
      <div v-if="step === 'edit'" class="flex-1 bg-white rounded-2xl p-5 shadow-sm space-y-4">
        <div class="flex items-center gap-2 mb-1">
          <span class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center shrink-0">
            <Check :size="12" class="text-white" />
          </span>
          <p class="text-sm font-bold text-gray-800">인식된 와인 정보</p>
        </div>

        <!-- 와인 이름 -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">와인 이름</label>
          <input
            v-model="form.name"
            class="w-full h-10 px-3 text-sm bg-gray-50 rounded-xl border border-gray-200 outline-none focus:border-[#722F37] transition"
            placeholder="와인 이름"
          />
        </div>

        <!-- 품종 + 빈티지 -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">품종</label>
            <input
              v-model="form.grape"
              class="w-full h-10 px-3 text-sm bg-gray-50 rounded-xl border border-gray-200 outline-none focus:border-[#722F37] transition"
              placeholder="카베르네 소비뇽"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">빈티지</label>
            <input
              v-model="form.vintage"
              type="number"
              class="w-full h-10 px-3 text-sm bg-gray-50 rounded-xl border border-gray-200 outline-none focus:border-[#722F37] transition"
              placeholder="2021"
            />
          </div>
        </div>

        <!-- 와인 타입 -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-2">종류</label>
          <div class="flex gap-2">
            <button
              v-for="type in wineTypes"
              :key="type.value"
              :class="[
                'flex-1 py-1.5 text-xs font-semibold rounded-xl border transition',
                form.type === type.value
                  ? 'bg-[#722F37] text-white border-[#722F37]'
                  : 'bg-gray-50 text-gray-600 border-gray-200'
              ]"
              @click="form.type = type.value"
            >
              {{ type.emoji }} {{ type.label }}
            </button>
          </div>
        </div>

        <!-- 맛 프로파일 슬라이더 -->
        <div class="space-y-3 pt-1">
          <p class="text-xs font-medium text-gray-500">맛 프로파일 (수정 가능)</p>
          <div v-for="item in tasteSliders" :key="item.key">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-gray-600">{{ item.emoji }} {{ item.label }}</span>
              <span class="text-xs font-bold text-[#722F37]">{{ form[item.key].toFixed(1) }}</span>
            </div>
            <Slider v-model="form[item.key]" />
          </div>
        </div>

        <!-- 등록 버튼 -->
        <Button
          class="w-full h-12 mt-2"
          :disabled="!form.name || isSubmitting"
          @click="handleSubmit"
        >
          {{ isSubmitting ? '등록 중...' : '🍾 내 컬렉션에 추가' }}
        </Button>
      </div>

      <!-- 촬영 전 안내 -->
      <div v-else-if="!previewImage" class="flex-1 flex flex-col items-center justify-center text-center pb-10">
        <p class="text-4xl mb-3">🍷</p>
        <p class="text-sm text-gray-500">와인 라벨을 촬영하면<br>품종, 지역, 빈티지를 자동으로 인식해요</p>
        <p class="text-xs text-gray-400 mt-2">메뉴 정보는 식당 DB에서 자동 제공됩니다</p>
      </div>
    </div>
  </div>
</template>
