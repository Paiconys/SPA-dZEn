<script setup>
import { inject } from 'vue'
import { toPublicUrl } from '../urlUtils.js'

defineProps({
  attachments: {
    type: Array,
    default: () => [],
  },
})

const openLightbox = inject('openLightbox')

function fileName(url) {
  try {
    return decodeURIComponent(toPublicUrl(url).split('/').pop())
  } catch {
    return url
  }
}

function isImage(url) {
  return /\.(jpe?g|png|gif)(\?|$)/i.test(toPublicUrl(url))
}
</script>

<template>
  <div v-if="attachments?.length" class="attachments">
    <button
      v-for="a in attachments"
      :key="a.id"
      type="button"
      class="att"
      :class="{ image: isImage(a.file) }"
      :title="fileName(a.file)"
      @click="openLightbox(a)"
    >
      <img
        v-if="isImage(a.file)"
        class="thumb"
        :src="toPublicUrl(a.file)"
        :alt="fileName(a.file)"
      />
      <span v-else class="file-link">📄 {{ fileName(a.file) }}</span>
    </button>
  </div>
</template>

<style scoped>
.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.5rem 0;
}

.att {
  border: 1px solid var(--border, #dde1e6);
  background: var(--header-bg, #f8f9fa);
  border-radius: 4px;
  padding: 0;
  cursor: pointer;
  overflow: hidden;
  max-width: 100%;
}

.att.image {
  line-height: 0;
}

.thumb {
  display: block;
  max-width: min(320px, 100%);
  max-height: 240px;
  width: auto;
  height: auto;
  object-fit: contain;
  vertical-align: middle;
}

.file-link {
  display: inline-block;
  padding: 0.4rem 0.65rem;
  font-size: 0.85rem;
  color: var(--accent-soft, #5a8bba);
}

.att:hover .file-link {
  text-decoration: underline;
}
</style>
