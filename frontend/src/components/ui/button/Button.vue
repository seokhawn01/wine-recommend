<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
  },
  size: {
    type: String,
    default: 'default',
  },
  as: {
    type: String,
    default: 'button',
  },
  class: String,
  disabled: Boolean,
})

const variantClasses = {
  default: 'bg-[#722F37] text-white hover:bg-[#5a2429] shadow',
  destructive: 'bg-destructive text-white hover:bg-destructive/90 shadow-sm',
  outline: 'border border-[#722F37] text-[#722F37] bg-white hover:bg-[#FFF8F0] shadow-sm',
  secondary: 'bg-[#FFF8F0] text-[#722F37] hover:bg-[#F5E8D8] shadow-sm',
  ghost: 'hover:bg-[#FFF8F0] hover:text-[#722F37]',
  link: 'text-[#722F37] underline-offset-4 hover:underline',
  gold: 'bg-[#C5A028] text-white hover:bg-[#a88620] shadow',
}

const sizeClasses = {
  default: 'h-9 px-4 py-2',
  sm: 'h-8 rounded-md px-3 text-xs',
  lg: 'h-10 rounded-md px-8',
  icon: 'h-9 w-9',
}

const computedClass = cn(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors',
  'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
  'disabled:pointer-events-none disabled:opacity-50',
  variantClasses[props.variant] || variantClasses.default,
  sizeClasses[props.size] || sizeClasses.default,
  props.class,
)
</script>

<template>
  <component
    :is="as"
    :class="computedClass"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>
