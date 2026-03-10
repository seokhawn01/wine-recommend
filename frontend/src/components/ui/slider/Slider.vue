<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  min: { type: Number, default: 0 },
  max: { type: Number, default: 5 },
  step: { type: Number, default: 0.1 },
  class: String,
  disabled: Boolean,
})

const emit = defineEmits(['update:modelValue'])

function onInput(e) {
  emit('update:modelValue', parseFloat(e.target.value))
}

const percentage = computed(() => ((props.modelValue - props.min) / (props.max - props.min)) * 100)
</script>

<template>
  <div :class="cn('relative w-full', props.class)">
    <input
      type="range"
      :min="min"
      :max="max"
      :step="step"
      :value="modelValue"
      :disabled="disabled"
      class="w-full h-2 appearance-none rounded-full cursor-pointer"
      :style="{
        background: `linear-gradient(to right, #722F37 ${percentage}%, #e5e7eb ${percentage}%)`
      }"
      @input="onInput"
    />
  </div>
</template>

<style scoped>
input[type='range']::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #722F37;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
input[type='range']::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #722F37;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
</style>
