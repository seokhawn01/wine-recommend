<script setup>
import { cn } from '@/lib/utils'
const props = defineProps({ class: String })
</script>
<template>
  <div :class="cn('inline-flex h-9 items-center justify-center rounded-lg bg-gray-100 p-1 text-muted-foreground w-full', props.class)">
    <slot />
  </div>
</template>
