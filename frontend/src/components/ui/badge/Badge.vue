<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: { type: String, default: 'default' },
  class: String,
})

const variantClasses = {
  default: 'bg-[#722F37] text-white hover:bg-[#5a2429]',
  secondary: 'bg-[#FFF8F0] text-[#722F37] hover:bg-[#F5E8D8]',
  outline: 'text-[#722F37] border border-[#722F37]',
  gold: 'bg-[#C5A028] text-white',
  destructive: 'bg-destructive text-white hover:bg-destructive/80',
  green: 'bg-green-100 text-green-700',
  gray: 'bg-gray-100 text-gray-600',
  selected: 'bg-[#722F37] text-white',
  unselected: 'bg-gray-100 text-gray-600 hover:bg-gray-200 cursor-pointer',
}
</script>

<template>
  <span
    :class="cn(
      'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
      'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
      variantClasses[variant] || variantClasses.default,
      props.class
    )"
  >
    <slot />
  </span>
</template>
