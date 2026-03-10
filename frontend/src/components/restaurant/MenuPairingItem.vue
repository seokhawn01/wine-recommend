<script setup>
defineProps({
  menu: {
    type: Object,
    required: true,
  },
})

function getPairingLevel(score) {
  if (score >= 0.8) return { label: '최상', color: '#C5A028', stars: 3 }
  if (score >= 0.5) return { label: '좋음', color: '#9CA3AF', stars: 2 }
  return { label: '보통', color: '#E5E7EB', stars: 1 }
}
</script>

<template>
  <div class="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 mb-0.5">
        <span class="font-medium text-gray-900 text-sm">{{ menu.name }}</span>
        <span class="text-xs text-gray-400 shrink-0">{{ menu.category }}</span>
      </div>
      <div class="text-xs text-gray-500 truncate">{{ menu.description }}</div>
      <div class="text-xs font-medium text-gray-700 mt-0.5">{{ menu.price.toLocaleString() }}원</div>
    </div>

    <!-- 페어링 점수 -->
    <div class="ml-3 flex flex-col items-center shrink-0">
      <div class="flex gap-0.5">
        <svg
          v-for="i in 3"
          :key="i"
          class="w-4 h-4"
          viewBox="0 0 24 24"
          :fill="i <= getPairingLevel(menu.pairingScore).stars ? getPairingLevel(menu.pairingScore).color : '#E5E7EB'"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </div>
      <span class="text-xs font-semibold mt-0.5" :style="{ color: getPairingLevel(menu.pairingScore).color }">
        {{ getPairingLevel(menu.pairingScore).label }}
      </span>
      <span class="text-xs text-gray-400">{{ Math.round(menu.pairingScore * 100) }}%</span>
    </div>
  </div>
</template>
