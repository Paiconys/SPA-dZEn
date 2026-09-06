<script setup>
import { onMounted, reactive, ref } from 'vue'

const emit = defineEmits(['created'])

const form = reactive({
  username: '',
  email: '',
  homepage: '',
  text: '',
  captcha: '',
  captcha_key: '',
})

const captchaImageUrl = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)
const textArea = ref(null)

async function loadCaptcha() {
  const res = await fetch('/api/captcha/')
  const data = await res.json()
  form.captcha_key = data.captcha_key
  form.captcha = ''
  captchaImageUrl.value = data.image_url
}

function wrapSelection(tag, attrs = '') {
  const el = textArea.value
  if (!el) return

  const start = el.selectionStart
  const end = el.selectionEnd
  const selected = form.text.slice(start, end) || 'text'
  const open = attrs ? `<${tag} ${attrs}>` : `<${tag}>`
  const close = `</${tag}>`
  const snippet = `${open}${selected}${close}`

  form.text = form.text.slice(0, start) + snippet + form.text.slice(end)

  requestAnimationFrame(() => {
    el.focus()
    const pos = start + snippet.length
    el.setSelectionRange(pos, pos)
  })
}

function insertLink() {
  const href = window.prompt('URL', 'https://')
  if (!href) return
  const title = window.prompt('Title (optional)', '') || ''
  const attrs = title
    ? `href="${href}" title="${title}"`
    : `href="${href}"`
  wrapSelection('a', attrs)
}

async function submitForm() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/comments/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: form.username,
        email: form.email,
        homepage: form.homepage || '',
        text: form.text,
        captcha_key: form.captcha_key,
        captcha: form.captcha,
        parent: null,
      }),
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = JSON.stringify(data)
      await loadCaptcha()
      return
    }
    success.value = `Created #${data.id}`
    form.text = ''
    form.captcha = ''
    emit('created')
    await loadCaptcha()
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadCaptcha)
</script>

<template>
  <form class="comment-form" @submit.prevent="submitForm">
    <h2>Add comment</h2>

    <label>
      User Name
      <input v-model="form.username" required />
    </label>

    <label>
      E-mail
      <input v-model="form.email" type="email" required />
    </label>

    <label>
      Home page
      <input v-model="form.homepage" type="url" placeholder="https://" />
    </label>

    <div class="tag-bar">
      <button type="button" @click="wrapSelection('i')">[i]</button>
      <button type="button" @click="wrapSelection('strong')">[strong]</button>
      <button type="button" @click="wrapSelection('code')">[code]</button>
      <button type="button" @click="insertLink">[a]</button>
    </div>

    <label>
      Text
      <textarea ref="textArea" v-model="form.text" required rows="4" />
    </label>

    <div class="preview">
      <h3>Preview</h3>
      <div class="preview-body" v-html="form.text || '<em>Nothing to preview</em>'" />
    </div>

    <div class="captcha">
      <img v-if="captchaImageUrl" :src="captchaImageUrl" alt="captcha" />
      <button type="button" @click="loadCaptcha">Refresh captcha</button>
      <label>
        CAPTCHA
        <input v-model="form.captcha" required />
      </label>
    </div>

    <button type="submit" :disabled="loading">Send</button>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="ok">{{ success }}</p>
  </form>
</template>

<style scoped>
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 28rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.tag-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.preview {
  border: 1px solid #ccc;
  padding: 0.75rem;
  border-radius: 4px;
}
.preview h3 {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
}
.preview-body {
  min-height: 2rem;
}
.error { color: #b00020; }
.ok { color: #0a7; }
.captcha img { max-width: 200px; }
</style>
