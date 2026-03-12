<script setup>
/**
 * TasteNebulaChart.vue
 * 취향 4가지 값(탄닌/산미/바디/당도)을 Canvas 성운(星雲)으로 시각화.
 * 값이 클수록 해당 방향 성운이 더 크고 밝게 표시됨.
 */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  tannin:    { type: Number, default: 2.5 }, // 왼쪽 상단 (보라)
  acidity:   { type: Number, default: 2.5 }, // 오른쪽 상단 (파랑)
  body:      { type: Number, default: 2.5 }, // 왼쪽 하단 (빨강)
  sweetness: { type: Number, default: 2.5 }, // 오른쪽 하단 (골드)
  size:      { type: Number, default: 280 },
})

const canvas = ref(null)
let animationId = null

// 각 속성별 성운 설정: 방향 + 색상
const NEBULAE = [
  { key: 'tannin',    angle: 225, color: [140, 80, 180] },  // 왼쪽 하단, 보라
  { key: 'acidity',  angle: 315, color: [70, 130, 200] },  // 오른쪽 하단, 파랑
  { key: 'body',     angle: 135, color: [180, 50, 70] },   // 왼쪽 상단, 와인레드
  { key: 'sweetness',angle: 45,  color: [197, 160, 40] },  // 오른쪽 상단, 골드
]

// 파티클 배열
let particles = []

function createParticles(cx, cy, radius) {
  particles = []
  NEBULAE.forEach((n) => {
    const value = props[n.key]          // 0~5
    const intensity = value / 5         // 0~1
    const count = Math.floor(intensity * 40) + 8
    const rad = (n.angle * Math.PI) / 180
    const spread = 0.8                  // 퍼짐 각도 (radian)

    for (let i = 0; i < count; i++) {
      const dist = (Math.random() * 0.6 + 0.15) * radius * intensity
      const angleOff = (Math.random() - 0.5) * spread
      const a = rad + angleOff
      particles.push({
        x: cx + Math.cos(a) * dist,
        y: cy + Math.sin(a) * dist,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        size: Math.random() * 3 + 1,
        alpha: Math.random() * 0.6 * intensity + 0.1,
        color: n.color,
        baseX: cx + Math.cos(a) * dist,
        baseY: cy + Math.sin(a) * dist,
        wobbleAmp: Math.random() * 8,
        wobbleSpeed: Math.random() * 0.02 + 0.005,
        wobbleOffset: Math.random() * Math.PI * 2,
      })
    }
  })
}

let frame = 0

function draw() {
  const c = canvas.value
  if (!c) return
  const ctx = c.getContext('2d')
  const dpr = window.devicePixelRatio || 1
  const w = c.width / dpr
  const h = c.height / dpr
  const cx = w / 2
  const cy = h / 2
  const radius = Math.min(w, h) * 0.42

  ctx.clearRect(0, 0, c.width, c.height)
  ctx.save()
  ctx.scale(dpr, dpr)

  // 1) 배경 글로우 — 각 속성별 방사형 그라디언트
  NEBULAE.forEach((n) => {
    const value = props[n.key]
    const intensity = value / 5
    if (intensity < 0.05) return

    const rad = (n.angle * Math.PI) / 180
    const dist = radius * 0.45
    const gx = cx + Math.cos(rad) * dist
    const gy = cy + Math.sin(rad) * dist
    const gr = radius * 0.6 * intensity

    const grad = ctx.createRadialGradient(gx, gy, 0, gx, gy, gr)
    const [r, g, b] = n.color
    grad.addColorStop(0, `rgba(${r},${g},${b},${0.25 * intensity})`)
    grad.addColorStop(0.5, `rgba(${r},${g},${b},${0.1 * intensity})`)
    grad.addColorStop(1, `rgba(${r},${g},${b},0)`)

    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(gx, gy, gr, 0, Math.PI * 2)
    ctx.fill()
  })

  // 2) 파티클 그리기 + 이동
  frame++
  particles.forEach((p) => {
    const wobble = Math.sin(frame * p.wobbleSpeed + p.wobbleOffset) * p.wobbleAmp
    const wx = p.baseX + Math.cos(frame * p.wobbleSpeed) * wobble
    const wy = p.baseY + Math.sin(frame * p.wobbleSpeed * 0.7) * wobble

    ctx.save()
    ctx.globalAlpha = p.alpha * (0.7 + 0.3 * Math.sin(frame * 0.03 + p.wobbleOffset))
    const [r, g, b] = p.color
    ctx.fillStyle = `rgb(${r},${g},${b})`
    ctx.shadowBlur = 4
    ctx.shadowColor = `rgba(${r},${g},${b},0.8)`
    ctx.beginPath()
    ctx.arc(wx, wy, p.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  })

  // 3) 중심 코어 글로우
  const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius * 0.18)
  coreGrad.addColorStop(0, 'rgba(255, 248, 240, 0.95)')
  coreGrad.addColorStop(0.4, 'rgba(197, 160, 40, 0.3)')
  coreGrad.addColorStop(1, 'rgba(197, 160, 40, 0)')
  ctx.fillStyle = coreGrad
  ctx.beginPath()
  ctx.arc(cx, cy, radius * 0.18, 0, Math.PI * 2)
  ctx.fill()

  // 4) 중심 라벨 (와인잔 이모지)
  ctx.font = `${radius * 0.18}px serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('🍷', cx, cy)

  ctx.restore()
  animationId = requestAnimationFrame(draw)
}

function initCanvas() {
  const c = canvas.value
  if (!c) return
  const dpr = window.devicePixelRatio || 1
  c.width = props.size * dpr
  c.height = props.size * dpr
  c.style.width = `${props.size}px`
  c.style.height = `${props.size}px`

  createParticles(props.size / 2, props.size / 2, (props.size / 2) * 0.9)
}

onMounted(() => {
  initCanvas()
  draw()
})

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
})

// 취향 값 변경 시 파티클 재생성
watch(
  () => [props.tannin, props.acidity, props.body, props.sweetness],
  () => {
    createParticles(props.size / 2, props.size / 2, (props.size / 2) * 0.9)
  }
)
</script>

<template>
  <canvas ref="canvas" class="block" />
</template>
