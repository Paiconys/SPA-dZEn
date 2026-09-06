<script setup>
import { computed, inject, reactive } from 'vue'
import AttachmentList from './AttachmentList.vue'
import CommentForm from './CommentForm.vue'

defineOptions({ name: 'CommentTable' })

const props = defineProps({
  comments: {
    type: Array,
    default: () => [],
  },
  sortable: {
    type: Boolean,
    default: false,
  },
  ordering: {
    type: String,
    default: '-created_at',
  },
  depth: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['set-ordering'])

const STEP_REM = 1.35
/** Peak indent to the right */
const MAX_STEPS = 3
/** Nested replies never go flatter than this (roots stay at 0) */
const MIN_STEPS = 1

/**
 * Pendulum: 1 → 2 → 3 → 2 → 1 → 2 → 3 → …
 * Bounces between MIN and MAX — never returns to full-width 0.
 */
function indentSteps(depth) {
  if (depth <= 0) return 0
  const range = MAX_STEPS - MIN_STEPS
  const period = range * 2
  const t = (depth - 1) % period
  if (t <= range) return MIN_STEPS + t
  return MAX_STEPS - (t - range)
}

const replyUi = inject('replyUi')
/** @type {Record<number, boolean>} */
const expanded = reactive({})

const shiftStyle = computed(() => {
  const steps = indentSteps(props.depth)
  if (!steps) return undefined
  return { marginLeft: `${steps * STEP_REM}rem` }
})

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
  <div class="comment-stack">
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

    <template v-for="c in comments" :key="c.id">
      <article
        class="comment-block"
        :class="{ shifted: indentSteps(depth) > 0 }"
        :style="shiftStyle"
      >
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
        </div>
      </article>

      <div v-if="replyUi.replyParentId.value === c.id" class="inline-form" :style="shiftStyle">
        <CommentForm
          compact
          :parent-id="c.id"
          :parent-label="c.username"
          @created="replyUi.onCreated"
          @cancel="replyUi.clearReply"
        />
      </div>

      <CommentTable
        v-if="expanded[c.id] && c.replies?.length"
        :comments="c.replies"
        :depth="depth + 1"
      />
    </template>
  </div>
</template>

<style scoped>
.comment-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  width: 100%;
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
  min-width: 0;
}

.comment-block.shifted {
  border-left: 3px solid #c5d8ea;
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
  overflow-wrap: anywhere;
}

.text {
  margin-bottom: 0.35rem;
  overflow-wrap: anywhere;
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

.inline-form {
  min-width: 0;
}
</style>
