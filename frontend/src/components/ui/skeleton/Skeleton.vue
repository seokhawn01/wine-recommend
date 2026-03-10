<script setup>
import { cn } from '@/lib/utils'
const props = defineProps({ class: String })
</script>
<template>
  <div :class="cn('animate-pulse rounded-md bg-gray-200', props.class)" />
</template>
