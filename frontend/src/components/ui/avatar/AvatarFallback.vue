<script setup>
import { cn } from '@/lib/utils'
const props = defineProps({ class: String })
</script>
<template>
  <span :class="cn('flex h-full w-full items-center justify-center rounded-full bg-[#FFF8F0] text-[#722F37] font-medium', props.class)">
    <slot />
  </span>
</template>
