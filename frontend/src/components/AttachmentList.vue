<script setup>
import { inject } from 'vue'

defineProps({
  attachments: {
    type: Array,
    default: () => [],
  },
})

const openLightbox = inject('openLightbox')

function fileName(url) {
  try {
    return decodeURIComponent(url.split('/').pop())
  } catch {
    return url
  }
}

function isImage(url) {
  return /\.(jpe?g|png|gif)(\?|$)/i.test(url)
}
</script>

<template>
  <div v-if="attachments?.length" class="attachments">
    <button
      v-for="a in attachments"
      :key="a.id"
      type="button"
      class="att"
      @click="openLightbox(a)"
    >
      {{ isImage(a.file) ? '🖼' : '📄' }}
      {{ fileName(a.file) }}
    </button>
  </div>
</template>

<style scoped>
.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0.35rem 0;
}
.att {
  font-size: 0.85rem;
  cursor: pointer;
}
</style>
