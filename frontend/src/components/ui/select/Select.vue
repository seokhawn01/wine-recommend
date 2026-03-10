<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  modelValue: [String, Number],
  class: String,
  placeholder: String,
  disabled: Boolean,
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <select
    :value="modelValue"
    :disabled="disabled"
    :class="cn(
      'flex h-9 w-full items-center justify-between whitespace-nowrap rounded-md border border-input',
      'bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background',
      'focus:outline-none focus:ring-1 focus:ring-[#722F37]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )"
    @change="emit('update:modelValue', $event.target.value)"
  >
    <option v-if="placeholder" value="" disabled :selected="!modelValue">{{ placeholder }}</option>
    <slot />
  </select>
</template>
