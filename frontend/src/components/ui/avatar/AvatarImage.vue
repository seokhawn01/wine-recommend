<script setup>
import { cn } from '@/lib/utils'
const props = defineProps({ class: String, src: String, alt: String })
</script>
<template>
  <img
    :src="src"
    :alt="alt"
    :class="cn('aspect-square h-full w-full object-cover', props.class)"
  />
</template>
