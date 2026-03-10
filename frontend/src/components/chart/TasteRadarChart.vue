<script setup>
import { computed } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps({
  tannin: { type: Number, default: 2.5 },
  acidity: { type: Number, default: 2.5 },
  body: { type: Number, default: 2.5 },
  sweetness: { type: Number, default: 2.5 },
  size: { type: String, default: 'md' }, // sm | md | lg
})

const chartData = computed(() => ({
  labels: ['타닌', '산미', '바디감', '당도'],
  datasets: [
    {
      label: '내 취향',
      data: [props.tannin, props.acidity, props.body, props.sweetness],
      backgroundColor: 'rgba(114, 47, 55, 0.2)',
      borderColor: '#722F37',
      borderWidth: 2,
      pointBackgroundColor: '#722F37',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#722F37',
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  scales: {
    r: {
      min: 0,
      max: 5,
      ticks: {
        stepSize: 1,
        display: false,
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.08)',
      },
      angleLines: {
        color: 'rgba(0, 0, 0, 0.1)',
      },
      pointLabels: {
        font: {
          size: 12,
          family: "'Noto Sans KR', sans-serif",
        },
        color: '#374151',
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.raw} / 5.0`,
      },
    },
  },
}

const sizeClass = {
  sm: 'w-32 h-32',
  md: 'w-48 h-48',
  lg: 'w-64 h-64',
}
</script>

<template>
  <div :class="['mx-auto', sizeClass[size] || sizeClass.md]">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>
