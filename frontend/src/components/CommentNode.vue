<script setup>
import AttachmentList from './AttachmentList.vue'

defineProps({
  comment: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['reply'])

function formatDate(value) {
  return new Date(value).toLocaleString()
}
</script>

<template>
  <li class="node">
    <div class="node-main">
      <strong>{{ comment.username }}</strong>
      <span class="meta">{{ comment.email }} · {{ formatDate(comment.created_at) }}</span>
      <div class="text" v-html="comment.text" />
      <AttachmentList :attachments="comment.attachments" />
      <button type="button" @click="emit('reply', comment)">Reply</button>
    </div>
    <ul v-if="comment.replies?.length" class="children">
      <CommentNode
        v-for="child in comment.replies"
        :key="child.id"
        :comment="child"
        @reply="emit('reply', $event)"
      />
    </ul>
  </li>
</template>

<style scoped>
.node {
  list-style: none;
  margin: 0.5rem 0;
}
.node-main {
  padding: 0.5rem 0.75rem;
  border-left: 3px solid #888;
  background: #f7f7f7;
}
.meta {
  display: block;
  font-size: 0.85rem;
  color: #555;
  margin-bottom: 0.35rem;
}
.children {
  margin: 0.25rem 0 0 1.25rem;
  padding: 0;
}
.text {
  margin-bottom: 0.35rem;
}
</style>
