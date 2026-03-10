<script setup>
import { inject } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({ value: String, class: String })
const { activeTab, setActiveTab } = inject('tabs')
</script>

<template>
  <button
    :class="cn(
      'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium',
      'ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2',
      'focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 flex-1',
      activeTab === value ? 'bg-white text-[#722F37] shadow' : 'hover:text-[#722F37]',
      props.class
    )"
    @click="setActiveTab(value)"
  >
    <slot />
  </button>
</template>
