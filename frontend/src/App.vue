<script setup>
import { ref } from 'vue'
import CommentForm from './components/CommentForm.vue'
import CommentList from './components/CommentList.vue'

const listRef = ref(null)

function onCreated() {
  listRef.value?.loadComments()
}
</script>

<template>
  <main>
    <h1>Comments</h1>
    <CommentList ref="listRef" />
    <CommentForm @created="onCreated" />
  </main>
</template>
