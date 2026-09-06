<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import AttachmentList from './AttachmentList.vue'
import CommentNode from './CommentNode.vue'

const emit = defineEmits(['reply'])

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
    comments.value = data.results
    count.value = data.count
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
  // Backend broadcasts new comment JSON; refresh list to keep tree/pagination correct
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

function orderingMark(field) {
  if (ordering.value === field) return ' ↑'
  if (ordering.value === `-${field}`) return ' ↓'
  return ''
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

function formatDate(value) {
  return new Date(value).toLocaleString()
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
  <section class="comment-table">
    <h2>Comments <small class="ws">WS: {{ wsStatus }}</small></h2>

    <p v-if="loading">Loading…</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table v-if="!loading && !error">
      <thead>
        <tr>
          <th>
            <button type="button" @click="setOrdering('username')">
              User Name{{ orderingMark('username') }}
            </button>
          </th>
          <th>
            <button type="button" @click="setOrdering('email')">
              E-mail{{ orderingMark('email') }}
            </button>
          </th>
          <th>
            <button type="button" @click="setOrdering('created_at')">
              Date{{ orderingMark('created_at') }}
            </button>
          </th>
          <th>Text / replies</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in comments" :key="c.id">
          <td>{{ c.username }}</td>
          <td>{{ c.email }}</td>
          <td>{{ formatDate(c.created_at) }}</td>
          <td>
            <div class="text" v-html="c.text" />
            <AttachmentList :attachments="c.attachments" />
            <button type="button" @click="emit('reply', c)">Reply</button>
            <ul v-if="c.replies?.length" class="tree">
              <CommentNode
                v-for="child in c.replies"
                :key="child.id"
                :comment="child"
                @reply="emit('reply', $event)"
              />
            </ul>
          </td>
        </tr>
        <tr v-if="comments.length === 0">
          <td colspan="4">No comments yet</td>
        </tr>
      </tbody>
    </table>

    <div class="pager" v-if="count > 0">
      <button type="button" :disabled="page <= 1" @click="prevPage">Prev</button>
      <span>Page {{ page }} / {{ totalPages() }} ({{ count }} total)</span>
      <button type="button" :disabled="page >= totalPages()" @click="nextPage">Next</button>
    </div>
  </section>
</template>

<style scoped>
.comment-table {
  margin-bottom: 2rem;
}
.ws {
  font-weight: normal;
  font-size: 0.85rem;
  color: #666;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  text-align: left;
  vertical-align: top;
}
th button {
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}
.pager {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-top: 0.75rem;
}
.error {
  color: #b00020;
}
.text {
  max-width: 24rem;
  margin-bottom: 0.35rem;
}
.tree {
  margin: 0.5rem 0 0;
  padding: 0;
}
</style>
