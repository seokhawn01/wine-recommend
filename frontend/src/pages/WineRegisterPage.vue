<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Slider from '@/components/ui/slider/Slider.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { useWineVision } from '@/composables/useWineVision'

const router = useRouter()
const { analyzeWineLabel, isLoading: isOcrLoading, error: visionError } = useWineVision()

// 와인 등록 폼 상태
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

const previewImage = ref(null)
const isSubmitting = ref(false)

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
    triggerVisionOcr(ev.target.result)
  }
  reader.readAsDataURL(file)
}

async function triggerVisionOcr(imageDataUrl) {
  const result = await analyzeWineLabel(imageDataUrl)
  if (!result) return // 에러는 visionError에 담김

  form.value.name = result.name
  form.value.grape = result.grape
  form.value.region = result.region
  form.value.vintage = result.vintage
  form.value.type = result.type
  form.value.tannin = result.tannin
  form.value.acidity = result.acidity
  form.value.body = result.body
  form.value.sweetness = result.sweetness
}

function handleSubmit() {
  if (!form.value.name) return
  isSubmitting.value = true
  setTimeout(() => {
    isSubmitting.value = false
    router.push('/mypage')
  }, 800)
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 페이지 헤더 -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
        <button
          class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
          @click="router.back()"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          마이페이지
        </button>
        <span class="text-gray-300">/</span>
        <span class="text-sm text-gray-800 font-medium">와인 등록</span>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-6 py-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-1">와인 컬렉션에 추가</h1>
        <p class="text-gray-500">라벨을 촬영하거나 직접 정보를 입력하세요.</p>
      </div>

      <Tabs default-value="ocr">
        <TabsList class="mb-6">
          <TabsTrigger value="ocr">📷 라벨 촬영</TabsTrigger>
          <TabsTrigger value="manual">✏️ 직접 입력</TabsTrigger>
        </TabsList>

        <!-- OCR 탭 -->
        <TabsContent value="ocr">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- 왼쪽: 이미지 업로드 -->
            <div class="space-y-4">
              <div class="bg-white rounded-xl p-6 shadow-sm">
                <h3 class="font-semibold text-gray-800 mb-4">와인 라벨 촬영/업로드</h3>

                <label class="block cursor-pointer">
                  <div
                    v-if="!previewImage"
                    class="border-2 border-dashed border-gray-200 rounded-xl h-64 flex flex-col items-center justify-center hover:border-[#722F37] hover:bg-[#FFF8F0] transition-colors"
                  >
                    <div class="text-5xl mb-3">📸</div>
                    <p class="text-base font-medium text-gray-700">사진을 업로드하세요</p>
                    <p class="text-sm text-gray-400 mt-1">클릭하거나 파일을 드래그하세요</p>
                    <p class="text-xs text-gray-300 mt-1">JPG, PNG · 최대 10MB</p>
                  </div>
                  <div v-else class="relative">
                    <img :src="previewImage" class="w-full h-64 object-contain rounded-xl bg-gray-50" alt="와인 라벨" />
                    <div class="absolute inset-0 bg-black/20 rounded-xl flex items-center justify-center">
                      <span class="text-white font-medium">다시 촬영</span>
                    </div>
                  </div>
                  <input type="file" accept="image/*" class="hidden" @change="handleImageUpload" />
                </label>

                <!-- Vision 분석 로딩 -->
                <div v-if="isOcrLoading" class="mt-4 flex items-center gap-2 text-sm text-gray-500">
                  <div class="w-4 h-4 border-2 border-[#722F37] border-t-transparent rounded-full animate-spin" />
                  GPT Vision으로 라벨 분석 중...
                </div>

                <!-- Vision 에러 -->
                <div v-if="visionError" class="mt-4 flex items-start gap-2 p-3 bg-red-50 rounded-xl border border-red-200">
                  <span class="text-red-500 text-base shrink-0">⚠️</span>
                  <div>
                    <p class="text-xs font-semibold text-red-700">라벨 인식 실패</p>
                    <p class="text-xs text-red-600 mt-0.5">{{ visionError }}</p>
                  </div>
                </div>

                <!-- Vision 결과 -->
                <div v-if="previewImage && !isOcrLoading && form.name" class="mt-4 p-4 bg-[#FFF8F0] rounded-xl border border-[#722F37]/10">
                  <p class="text-xs font-semibold text-[#722F37] mb-2">✅ 인식된 정보</p>
                  <p class="font-semibold text-gray-900">{{ form.name }}</p>
                  <p class="text-sm text-gray-600 mt-1">{{ form.grape }} · {{ form.region }}</p>
                </div>
              </div>
            </div>

            <!-- 오른쪽: 맛 프로파일 조정 -->
            <div v-if="form.name" class="space-y-4">
              <div class="bg-white rounded-xl p-6 shadow-sm">
                <h3 class="font-semibold text-gray-800 mb-5">맛 프로파일 조정</h3>
                <div class="space-y-5">
                  <div v-for="item in tasteSliders" :key="item.key">
                    <div class="flex justify-between mb-2">
                      <span class="text-sm text-gray-700">{{ item.emoji }} {{ item.label }}</span>
                      <span class="text-sm font-bold text-[#722F37]">{{ form[item.key].toFixed(1) }}</span>
                    </div>
                    <Slider v-model="form[item.key]" />
                  </div>
                </div>

                <Button
                  class="w-full h-12 mt-6 text-base"
                  :disabled="isSubmitting"
                  @click="handleSubmit"
                >
                  {{ isSubmitting ? '등록 중...' : '와인 등록 완료' }}
                </Button>
              </div>
            </div>

            <!-- OCR 전 안내 -->
            <div v-else class="bg-white rounded-xl p-6 shadow-sm flex flex-col items-center justify-center text-center h-64">
              <div class="text-4xl mb-3">🍷</div>
              <p class="text-gray-500 text-sm">라벨을 업로드하면<br>맛 프로파일 조정 옵션이 표시됩니다.</p>
            </div>
          </div>
        </TabsContent>

        <!-- 수동 입력 탭 -->
        <TabsContent value="manual">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- 왼쪽: 기본 정보 -->
            <div class="bg-white rounded-xl p-6 shadow-sm">
              <h3 class="font-semibold text-gray-800 mb-5">와인 기본 정보</h3>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">와인 이름 *</label>
                  <Input v-model="form.name" placeholder="예: 샤토 마르고 2018" class="h-11" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">품종</label>
                  <Input v-model="form.grape" placeholder="예: 카베르네 소비뇽" class="h-11" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">원산지/지역</label>
                  <Input v-model="form.region" placeholder="예: 보르도, 프랑스" class="h-11" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">빈티지 (출시연도)</label>
                  <Input v-model="form.vintage" type="number" placeholder="예: 2020" class="h-11" />
                </div>

                <!-- 와인 타입 선택 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">와인 종류</label>
                  <div class="flex gap-2 flex-wrap">
                    <Badge
                      v-for="type in wineTypes"
                      :key="type.value"
                      :variant="form.type === type.value ? 'selected' : 'unselected'"
                      class="cursor-pointer py-2 px-4 text-sm border-0"
                      @click="form.type = type.value"
                    >
                      {{ type.emoji }} {{ type.label }}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>

            <!-- 오른쪽: 맛 프로파일 -->
            <div class="bg-white rounded-xl p-6 shadow-sm">
              <h3 class="font-semibold text-gray-800 mb-5">맛 프로파일</h3>
              <div class="space-y-5">
                <div v-for="item in tasteSliders" :key="item.key">
                  <div class="flex justify-between mb-2">
                    <span class="text-sm text-gray-700">{{ item.emoji }} {{ item.label }}</span>
                    <span class="text-sm font-bold text-[#722F37]">{{ form[item.key].toFixed(1) }}</span>
                  </div>
                  <Slider v-model="form[item.key]" />
                </div>
              </div>

              <Button
                class="w-full h-12 mt-6 text-base"
                :disabled="!form.name || isSubmitting"
                @click="handleSubmit"
              >
                {{ isSubmitting ? '등록 중...' : '와인 등록 완료' }}
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  </div>
</template>
