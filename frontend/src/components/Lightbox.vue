<script setup>
defineProps({
  open: Boolean,
  url: { type: String, default: '' },
  title: { type: String, default: '' },
  isImage: { type: Boolean, default: true },
  textContent: { type: String, default: '' },
})

const emit = defineEmits(['close'])

function onKey(e) {
  if (e.key === 'Escape') emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="overlay"
      tabindex="0"
      @click.self="emit('close')"
      @keydown="onKey"
    >
      <div class="panel">
        <button type="button" class="close" @click="emit('close')">×</button>
        <p v-if="title" class="title">{{ title }}</p>
        <img v-if="isImage && url" :src="url" :alt="title" />
        <pre v-else-if="textContent" class="txt">{{ textContent }}</pre>
        <p v-else>
          <a :href="url" target="_blank" rel="noopener">Open file</a>
        </p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.panel {
  position: relative;
  max-width: min(90vw, 800px);
  max-height: 90vh;
  overflow: auto;
  background: #111;
  color: #eee;
  padding: 1.5rem;
  border-radius: 8px;
}
.panel img {
  max-width: 100%;
  height: auto;
  display: block;
}
.close {
  position: absolute;
  top: 0.35rem;
  right: 0.5rem;
  border: none;
  background: transparent;
  color: #fff;
  font-size: 1.75rem;
  cursor: pointer;
  line-height: 1;
}
.title {
  margin: 0 1.5rem 0.75rem 0;
  font-size: 0.9rem;
}
.txt {
  white-space: pre-wrap;
  margin: 0;
  font-family: ui-monospace, monospace;
}
</style>
