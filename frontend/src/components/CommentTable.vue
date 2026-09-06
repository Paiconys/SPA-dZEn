<script setup>
import { inject, reactive } from 'vue'
import AttachmentList from './AttachmentList.vue'
import CommentForm from './CommentForm.vue'

defineOptions({ name: 'CommentTable' })

const props = defineProps({
  comments: {
    type: Array,
    default: () => [],
  },
  /** Root list: show sort controls */
  sortable: {
    type: Boolean,
    default: false,
  },
  ordering: {
    type: String,
    default: '-created_at',
  },
})

const emit = defineEmits(['set-ordering'])

const replyUi = inject('replyUi')
/** @type {Record<number, boolean>} */
const expanded = reactive({})

function countReplies(node) {
  if (!node.replies?.length) return 0
  return node.replies.reduce((sum, child) => sum + 1 + countReplies(child), 0)
}

function toggleReplies(id) {
  expanded[id] = !expanded[id]
}

function formatDate(value) {
  return new Date(value).toLocaleString()
}

function orderingMark(field) {
  if (props.ordering === field) return ' ↑'
  if (props.ordering === `-${field}`) return ' ↓'
  return ''
}
</script>

<template>
  <div class="comment-stack" :class="{ nested: !sortable }">
    <div v-if="sortable" class="sort-bar">
      <span class="sort-label">Sort by</span>
      <button type="button" @click="emit('set-ordering', 'username')">
        User Name{{ orderingMark('username') }}
      </button>
      <button type="button" @click="emit('set-ordering', 'email')">
        E-mail{{ orderingMark('email') }}
      </button>
      <button type="button" @click="emit('set-ordering', 'created_at')">
        Date{{ orderingMark('created_at') }}
      </button>
    </div>

    <p v-if="comments.length === 0" class="empty">No comments yet</p>

    <article v-for="c in comments" :key="c.id" class="comment-block">
      <header class="comment-head">
        <span class="username">{{ c.username }}</span>
        <span class="email">{{ c.email }}</span>
        <span class="date">{{ formatDate(c.created_at) }}</span>
        <a
          v-if="c.homepage"
          class="homepage"
          :href="c.homepage"
          target="_blank"
          rel="noopener noreferrer"
        >{{ c.homepage }}</a>
      </header>

      <div class="comment-body">
        <div class="text" v-html="c.text" />
        <AttachmentList :attachments="c.attachments" />
        <div class="row-actions">
          <button
            v-if="c.replies?.length"
            type="button"
            class="link-btn"
            @click="toggleReplies(c.id)"
          >
            {{
              expanded[c.id]
                ? 'Свернуть ответы'
                : `Развернуть ответы (${countReplies(c)})`
            }}
          </button>
          <button
            type="button"
            class="link-btn reply"
            :class="{ active: replyUi.replyParentId.value === c.id }"
            @click="replyUi.startReply(c)"
          >
            ↩ Reply
          </button>
        </div>

        <CommentForm
          v-if="replyUi.replyParentId.value === c.id"
          compact
          :parent-id="c.id"
          :parent-label="c.username"
          @created="replyUi.onCreated"
          @cancel="replyUi.clearReply"
        />

        <CommentTable
          v-if="expanded[c.id] && c.replies?.length"
          :comments="c.replies"
        />
      </div>
    </article>
  </div>
</template>

<style scoped>
.comment-stack {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.comment-stack.nested {
  margin: 0.65rem 0 0.15rem 1.25rem;
  gap: 0.65rem;
}

.sort-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.85rem;
  padding: 0.55rem 0.75rem;
  background: var(--header-bg, #f8f9fa);
  border: 1px solid var(--border, #dde1e6);
  border-radius: var(--radius, 6px);
  margin-bottom: 0.25rem;
}

.sort-label {
  font-size: 0.85rem;
  color: var(--text-muted, #888);
  margin-right: 0.25rem;
}

.sort-bar button {
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  font-weight: 600;
  font-size: 0.92rem;
  cursor: pointer;
  color: var(--accent, #3b6ea5);
}

.sort-bar button:hover {
  text-decoration: underline;
}

.empty {
  margin: 0;
  color: var(--text-muted, #888);
}

.comment-block {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #dde1e6);
  border-radius: var(--radius, 6px);
  overflow: hidden;
}

.comment-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.45rem 1rem;
  padding: 0.55rem 0.9rem;
  background: var(--header-bg, #f8f9fa);
  border-bottom: 1px solid var(--border, #dde1e6);
}

.username {
  font-weight: 600;
  color: #111;
}

.email,
.date {
  font-size: 0.88rem;
  color: var(--text-muted, #888);
}

.date {
  white-space: nowrap;
}

.homepage {
  max-width: 14rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.85rem;
  color: var(--accent-soft, #5a8bba);
}

.comment-body {
  padding: 0.85rem 0.95rem 0.95rem;
  background: #fff;
  color: #222;
  line-height: 1.5;
}

.text {
  margin-bottom: 0.35rem;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1.1rem;
  margin-top: 0.55rem;
}

.link-btn {
  border: none;
  background: transparent;
  color: var(--accent-soft, #5a8bba);
  padding: 0;
  font-size: 0.9rem;
}

.link-btn:hover,
.link-btn.active {
  color: var(--accent, #3b6ea5);
  text-decoration: underline;
}

.link-btn.reply {
  margin-left: auto;
}
</style>
