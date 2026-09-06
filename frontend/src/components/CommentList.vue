<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { buildCommentTree } from '../commentTree.js'
import CommentTable from './CommentTable.vue'

const comments = ref([])
const count = ref(0)
const page = ref(1)
const ordering = ref('-created_at')
const loading = ref(false)
const error = ref('')
const wsStatus = ref('off')

const pageSize = 25
let socket = null

async function loadComments() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({
      page: String(page.value),
      ordering: ordering.value,
    })
    const res = await fetch(`/api/comments/?${params}`)
    const data = await res.json()
    if (!res.ok) {
      error.value = JSON.stringify(data)
      return
    }
    comments.value = buildCommentTree(data.results || [])
    // Prefer server count when API already returns roots only;
    // if payload mixes replies in, count roots on this page at least.
    const rootOnly = (data.results || []).every(
      (c) => c.parent == null || c.parent === undefined,
    )
    count.value = rootOnly ? data.count : comments.value.length
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
}

function connectWs() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url = `${protocol}//${window.location.host}/ws/comments/`
  socket = new WebSocket(url)

  socket.onopen = () => {
    wsStatus.value = 'on'
  }
  socket.onclose = () => {
    wsStatus.value = 'off'
  }
  socket.onerror = () => {
    wsStatus.value = 'error'
  }
  socket.onmessage = () => {
    loadComments()
  }
}

function setOrdering(field) {
  if (ordering.value === field) {
    ordering.value = `-${field}`
  } else if (ordering.value === `-${field}`) {
    ordering.value = field
  } else {
    ordering.value = field
  }
  page.value = 1
  loadComments()
}

const totalPages = () => Math.max(1, Math.ceil(count.value / pageSize))

function prevPage() {
  if (page.value <= 1) return
  page.value -= 1
  loadComments()
}

function nextPage() {
  if (page.value >= totalPages()) return
  page.value += 1
  loadComments()
}

onMounted(() => {
  loadComments()
  connectWs()
})

onUnmounted(() => {
  socket?.close()
})

defineExpose({ loadComments })
</script>

<template>
  <section class="comment-list">
    <div class="section-head">
      <h2>Comments</h2>
      <small class="ws" :class="wsStatus">WS: {{ wsStatus }}</small>
    </div>

    <p v-if="loading">Loading…</p>
    <p v-if="error" class="error">{{ error }}</p>

    <CommentTable
      v-if="!loading && !error"
      sortable
      :comments="comments"
      :ordering="ordering"
      @set-ordering="setOrdering"
    />

    <div class="pager" v-if="count > 0">
      <button type="button" :disabled="page <= 1" @click="prevPage">Prev</button>
      <span>Page {{ page }} / {{ totalPages() }} ({{ count }} total)</span>
      <button type="button" :disabled="page >= totalPages()" @click="nextPage">Next</button>
    </div>
  </section>
</template>

<style scoped>
.comment-list {
  margin-bottom: 2rem;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #dde1e6);
  border-radius: var(--radius, 6px);
  padding: 1rem 1.1rem 1.25rem;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.ws {
  font-size: 0.85rem;
  color: var(--text-muted, #888);
}
.ws.on {
  color: var(--ok, #0a7a4b);
}
.ws.error {
  color: var(--danger, #b00020);
}

.pager {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-top: 0.9rem;
}

.pager button {
  border: 1px solid var(--border, #dde1e6);
  background: var(--header-bg, #f8f9fa);
  border-radius: 4px;
  padding: 0.35rem 0.7rem;
}

.error {
  color: var(--danger, #b00020);
}
</style>
