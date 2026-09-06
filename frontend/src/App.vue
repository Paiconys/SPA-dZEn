<script setup>
import { provide, reactive, ref } from 'vue'
import CommentForm from './components/CommentForm.vue'
import CommentList from './components/CommentList.vue'
import Lightbox from './components/Lightbox.vue'

const listRef = ref(null)
const replyParentId = ref(null)
const replyParentLabel = ref('')

const lightbox = reactive({
  open: false,
  url: '',
  title: '',
  isImage: true,
  textContent: '',
})

async function openLightbox(attachment) {
  const url = attachment.file
  const name = decodeURIComponent(url.split('/').pop() || 'file')
  const isImage = /\.(jpe?g|png|gif)(\?|$)/i.test(url)

  lightbox.url = url
  lightbox.title = name
  lightbox.isImage = isImage
  lightbox.textContent = ''

  if (!isImage && /\.txt(\?|$)/i.test(url)) {
    try {
      const res = await fetch(url)
      lightbox.textContent = await res.text()
    } catch {
      lightbox.textContent = 'Could not load text file.'
    }
  }

  lightbox.open = true
}

function closeLightbox() {
  lightbox.open = false
}

provide('openLightbox', openLightbox)

function onCreated() {
  replyParentId.value = null
  replyParentLabel.value = ''
  listRef.value?.loadComments()
}

function onReply(comment) {
  replyParentId.value = comment.id
  replyParentLabel.value = comment.username
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

function clearReply() {
  replyParentId.value = null
  replyParentLabel.value = ''
}
</script>

<template>
  <main>
    <h1>Comments</h1>
    <CommentList ref="listRef" @reply="onReply" />
    <div v-if="replyParentId" class="reply-bar">
      <span>Reply mode: #{{ replyParentId }} ({{ replyParentLabel }})</span>
      <button type="button" @click="clearReply">Cancel reply</button>
    </div>
    <CommentForm
      :parent-id="replyParentId"
      :parent-label="replyParentLabel"
      @created="onCreated"
    />
    <Lightbox
      :open="lightbox.open"
      :url="lightbox.url"
      :title="lightbox.title"
      :is-image="lightbox.isImage"
      :text-content="lightbox.textContent"
      @close="closeLightbox"
    />
  </main>
</template>

<style scoped>
.reply-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.75rem;
}
</style>
