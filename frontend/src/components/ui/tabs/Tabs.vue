<script setup>
import { provide, ref } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  defaultValue: String,
  modelValue: String,
  class: String,
})

const emit = defineEmits(['update:modelValue'])

const activeTab = ref(props.modelValue || props.defaultValue || '')

provide('tabs', {
  activeTab,
  setActiveTab: (val) => {
    activeTab.value = val
    emit('update:modelValue', val)
  },
})
</script>

<template>
  <div :class="cn('w-full', props.class)">
    <slot />
  </div>
</template>
