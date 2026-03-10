<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  class: String,
  placeholder: String,
  disabled: Boolean,
  modelValue: String,
  rows: { type: Number, default: 3 },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <textarea
    :placeholder="placeholder"
    :disabled="disabled"
    :rows="rows"
    :value="modelValue"
    :class="cn(
      'flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm',
      'placeholder:text-muted-foreground',
      'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#722F37]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )"
    @input="emit('update:modelValue', $event.target.value)"
  />
</template>
