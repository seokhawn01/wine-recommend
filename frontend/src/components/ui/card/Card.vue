<script setup>
import { cn } from '@/lib/utils'
const props = defineProps({ class: String })
</script>
<template>
  <div :class="cn('rounded-xl border bg-white text-card-foreground shadow', props.class)">
    <slot />
  </div>
</template>
