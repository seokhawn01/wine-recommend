<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  class: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  disabled: Boolean,
  modelValue: [String, Number],
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <input
    :type="type"
    :placeholder="placeholder"
    :disabled="disabled"
    :value="modelValue"
    :class="cn(
      'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm',
      'transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium',
      'placeholder:text-muted-foreground',
      'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#722F37]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )"
    @input="emit('update:modelValue', $event.target.value)"
    v-bind="$attrs"
  />
</template>
