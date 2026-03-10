<script setup>
import Badge from '@/components/ui/badge/Badge.vue'

defineProps({
  wine: {
    type: Object,
    required: true,
  },
  compact: { type: Boolean, default: false },
})

const wineTypeLabel = {
  red: { label: '레드', color: '#722F37', emoji: '🍷' },
  white: { label: '화이트', color: '#C5A028', emoji: '🥂' },
  sparkling: { label: '스파클링', color: '#6B7280', emoji: '🍾' },
  rose: { label: '로제', color: '#E879A0', emoji: '🌸' },
}
</script>

<template>
  <!-- 컴팩트 버전 (목록용) -->
  <div v-if="compact" class="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-100">
    <div class="w-10 h-10 rounded-full flex items-center justify-center text-xl shrink-0"
      :style="{ backgroundColor: `${wineTypeLabel[wine.type]?.color}15` }">
      {{ wineTypeLabel[wine.type]?.emoji || '🍷' }}
    </div>
    <div class="flex-1 min-w-0">
      <div class="font-medium text-sm text-gray-900 truncate">{{ wine.name }}</div>
      <div class="text-xs text-gray-500">{{ wine.grape }} · {{ wine.region }}</div>
    </div>
    <Badge :variant="wine.type === 'red' ? 'default' : 'secondary'" class="shrink-0 text-xs">
      {{ wineTypeLabel[wine.type]?.label || '와인' }}
    </Badge>
  </div>

  <!-- 풀 카드 버전 -->
  <div v-else class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
    <!-- 상단 컬러 배너 -->
    <div class="h-16 flex items-center justify-center text-4xl"
      :style="{ background: `linear-gradient(135deg, ${wineTypeLabel[wine.type]?.color}20, ${wineTypeLabel[wine.type]?.color}40)` }">
      {{ wineTypeLabel[wine.type]?.emoji || '🍷' }}
    </div>

    <div class="p-3">
      <div class="flex items-start justify-between mb-1">
        <h3 class="font-semibold text-gray-900 text-sm leading-tight flex-1 mr-2">{{ wine.name }}</h3>
        <Badge :variant="wine.type === 'red' ? 'default' : 'secondary'" class="text-xs shrink-0">
          {{ wineTypeLabel[wine.type]?.label || '와인' }}
        </Badge>
      </div>

      <p class="text-xs text-gray-500 mb-2">{{ wine.grape }} · {{ wine.region }}
        <span v-if="wine.vintage"> · {{ wine.vintage }}</span>
      </p>

      <!-- 맛 프로파일 바 -->
      <div class="space-y-1">
        <div v-for="(val, key) in { 타닌: wine.tannin, 산미: wine.acidity, 바디: wine.body, 당도: wine.sweetness }"
          :key="key" class="flex items-center gap-2">
          <span class="text-xs text-gray-500 w-8 shrink-0">{{ key }}</span>
          <div class="flex-1 bg-gray-100 rounded-full h-1.5">
            <div
              class="h-1.5 rounded-full transition-all"
              :style="{ width: `${(val / 5) * 100}%`, backgroundColor: '#722F37' }"
            />
          </div>
          <span class="text-xs text-gray-400 w-5 text-right">{{ val }}</span>
        </div>
      </div>

      <!-- 향 태그 -->
      <div v-if="wine.aroma?.length" class="flex flex-wrap gap-1 mt-2">
        <Badge v-for="a in wine.aroma" :key="a" variant="gray" class="text-xs">{{ a }}</Badge>
      </div>
    </div>
  </div>
</template>
