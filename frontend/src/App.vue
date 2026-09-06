<script setup>
import { provide, reactive, ref } from 'vue'
import CommentForm from './components/CommentForm.vue'
import CommentList from './components/CommentList.vue'
import Lightbox from './components/Lightbox.vue'

const listRef = ref(null)
const replyParentId = ref(null)
const replyParentLabel = ref('')
const showNewDiscussion = ref(false)

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

function clearReply() {
  replyParentId.value = null
  replyParentLabel.value = ''
}

function closeNewDiscussion() {
  showNewDiscussion.value = false
}

function openNewDiscussion() {
  clearReply()
  showNewDiscussion.value = true
}

function startReply(comment) {
  closeNewDiscussion()
  if (replyParentId.value === comment.id) {
    clearReply()
    return
  }
  replyParentId.value = comment.id
  replyParentLabel.value = comment.username
}

function onCreated() {
  clearReply()
  closeNewDiscussion()
  listRef.value?.loadComments()
}

provide('replyUi', {
  replyParentId,
  replyParentLabel,
  startReply,
  clearReply,
  onCreated,
})
</script>

<template>
  <main class="page">
    <header class="page-head">
      <h1>Comments</h1>
      <button
        v-if="!showNewDiscussion"
        type="button"
        class="add-btn"
        @click="openNewDiscussion"
      >
        Добавить обсуждение
      </button>
    </header>

    <CommentForm
      v-if="showNewDiscussion"
      @created="onCreated"
      @cancel="closeNewDiscussion"
    />

    <CommentList ref="listRef" />

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
.page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1rem;
}

.page-head h1 {
  margin: 0;
  flex: 1;
}

.add-btn {
  border: none;
  border-radius: 4px;
  padding: 0.5rem 0.95rem;
  background: var(--accent, #3b6ea5);
  color: #fff;
  font-weight: 600;
}

.add-btn:hover {
  filter: brightness(1.05);
}
</style>
