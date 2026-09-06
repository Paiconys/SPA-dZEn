<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { previewHtml, validateTagBalance } from '../htmlUtils.js'

const emit = defineEmits(['created', 'cancel'])

const props = defineProps({
  parentId: {
    type: [Number, null],
    default: null,
  },
  parentLabel: {
    type: String,
    default: '',
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

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
const fieldErrors = reactive({
  username: '',
  email: '',
  homepage: '',
  text: '',
  captcha: '',
  file: '',
})
const success = ref('')
const loading = ref(false)
const textArea = ref(null)
const fileInput = ref(null)
const selectedFile = ref(null)

function onFileChange(e) {
  selectedFile.value = e.target.files?.[0] || null
  fieldErrors.file = ''
}

function clearFieldErrors() {
  fieldErrors.username = ''
  fieldErrors.email = ''
  fieldErrors.homepage = ''
  fieldErrors.text = ''
  fieldErrors.captcha = ''
  fieldErrors.file = ''
}

function validateClient() {
  clearFieldErrors()
  let ok = true

  const username = form.username.trim()
  if (!username) {
    fieldErrors.username = 'Required'
    ok = false
  } else if (!/^[a-zA-Z0-9]+$/.test(username)) {
    fieldErrors.username = 'Only latin letters and digits'
    ok = false
  }

  const email = form.email.trim()
  if (!email) {
    fieldErrors.email = 'Required'
    ok = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    fieldErrors.email = 'Invalid email'
    ok = false
  }

  const homepage = form.homepage.trim()
  if (homepage) {
    try {
      const url = new URL(homepage)
      if (url.protocol !== 'http:' && url.protocol !== 'https:') {
        fieldErrors.homepage = 'URL must start with http:// or https://'
        ok = false
      }
    } catch {
      fieldErrors.homepage = 'Invalid URL'
      ok = false
    }
  }

  if (!form.text.trim()) {
    fieldErrors.text = 'Required'
    ok = false
  } else {
    const balanceError = validateTagBalance(form.text)
    if (balanceError) {
      fieldErrors.text = balanceError
      ok = false
    }
  }

  const captcha = form.captcha.trim()
  if (!captcha) {
    fieldErrors.captcha = 'Required'
    ok = false
  } else if (!/^[a-zA-Z0-9]+$/.test(captcha)) {
    fieldErrors.captcha = 'Only latin letters and digits'
    ok = false
  }

  if (selectedFile.value) {
    const name = selectedFile.value.name.toLowerCase()
    const allowed = ['.jpg', '.jpeg', '.gif', '.png', '.txt']
    if (!allowed.some((ext) => name.endsWith(ext))) {
      fieldErrors.file = 'Only JPG, GIF, PNG or TXT'
      ok = false
    } else if (name.endsWith('.txt') && selectedFile.value.size > 100 * 1024) {
      fieldErrors.file = 'TXT must be at most 100 KB'
      ok = false
    }
  }

  return ok
}

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
  if (!validateClient()) {
    return
  }
  loading.value = true
  try {
    const body = new FormData()
    body.append('username', form.username)
    body.append('email', form.email)
    if (form.homepage.trim()) {
      body.append('homepage', form.homepage.trim())
    }
    body.append('text', form.text)
    body.append('captcha_key', form.captcha_key)
    body.append('captcha', form.captcha)
    if (props.parentId != null) {
      body.append('parent', String(props.parentId))
    }
    if (selectedFile.value) {
      body.append('file', selectedFile.value)
    }

    const res = await fetch('/api/comments/', {
      method: 'POST',
      body,
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
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    emit('created', data)
    await loadCaptcha()
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
}

const preview = computed(() => previewHtml(form.text))

onMounted(loadCaptcha)
</script>

<template>
  <form class="comment-form" :class="{ compact }" @submit.prevent="submitForm">
    <div class="form-head">
      <h2>{{ parentId ? `Reply to #${parentId}` : 'Add comment' }}</h2>
      <button type="button" class="ghost cancel" @click="emit('cancel')">
        Cancel
      </button>
    </div>
    <p v-if="parentLabel" class="reply-hint">Replying to {{ parentLabel }}</p>

    <label>
      User Name
      <input v-model="form.username" required />
      <span v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</span>
    </label>

    <label>
      E-mail
      <input v-model="form.email" type="email" required />
      <span v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</span>
    </label>

    <label>
      Home page <span class="optional">(optional)</span>
      <input v-model="form.homepage" type="text" inputmode="url" placeholder="https://" />
      <span v-if="fieldErrors.homepage" class="field-error">{{ fieldErrors.homepage }}</span>
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
      <span v-if="fieldErrors.text" class="field-error">{{ fieldErrors.text }}</span>
    </label>

    <div class="preview">
      <h3>Preview</h3>
      <div class="preview-body" v-html="preview" />
    </div>

    <label>
      Attachment (JPG/GIF/PNG or TXT ≤ 100KB)
      <input
        ref="fileInput"
        type="file"
        accept=".jpg,.jpeg,.gif,.png,.txt,image/jpeg,image/gif,image/png,text/plain"
        @change="onFileChange"
      />
      <span v-if="fieldErrors.file" class="field-error">{{ fieldErrors.file }}</span>
    </label>

    <div class="captcha">
      <img v-if="captchaImageUrl" :src="captchaImageUrl" alt="captcha" />
      <button type="button" class="ghost" @click="loadCaptcha">Refresh captcha</button>
      <label>
        CAPTCHA
        <input v-model="form.captcha" required />
        <span v-if="fieldErrors.captcha" class="field-error">{{ fieldErrors.captcha }}</span>
      </label>
    </div>

    <button type="submit" class="submit" :disabled="loading">Send</button>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="ok">{{ success }}</p>
  </form>
</template>

<style scoped>
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  max-width: 32rem;
  padding: 1.1rem 1.2rem 1.35rem;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #dde1e6);
  border-radius: var(--radius, 6px);
}

.comment-form.compact {
  max-width: none;
  margin: 0.65rem 0 0.35rem;
  padding: 0.85rem 1rem 1rem;
}

.form-head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.form-head h2 {
  margin: 0;
  flex: 1;
}

.cancel {
  margin-left: auto;
}

.reply-hint {
  margin: 0;
  color: var(--text-muted, #888);
  font-size: 0.9rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.92rem;
}

.optional {
  color: var(--text-muted, #888);
  font-weight: 400;
  font-size: 0.85em;
}

input,
textarea {
  border: 1px solid var(--border, #dde1e6);
  border-radius: 4px;
  padding: 0.45rem 0.55rem;
  background: #fff;
}

input:focus,
textarea:focus {
  outline: 2px solid color-mix(in srgb, var(--accent-soft, #5a8bba) 45%, white);
  outline-offset: 1px;
}

.tag-bar {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.tag-bar button,
.ghost {
  border: 1px solid var(--border, #dde1e6);
  background: var(--header-bg, #f8f9fa);
  border-radius: 4px;
  padding: 0.3rem 0.55rem;
  color: var(--accent, #3b6ea5);
}

.preview {
  border: 1px solid var(--border, #dde1e6);
  background: var(--header-bg, #f8f9fa);
  padding: 0.75rem;
  border-radius: 4px;
}

.preview h3 {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
}

.preview-body {
  min-height: 2rem;
  line-height: 1.5;
}

.preview-body :deep(.preview-error) {
  color: var(--danger, #b00020);
  font-size: 0.9rem;
}

.captcha {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.captcha img {
  max-width: 200px;
  border: 1px solid var(--border, #dde1e6);
  border-radius: 4px;
}

.submit {
  align-self: flex-start;
  border: none;
  border-radius: 4px;
  padding: 0.55rem 1.1rem;
  background: var(--accent, #3b6ea5);
  color: #fff;
  font-weight: 600;
}

.submit:hover:not(:disabled) {
  filter: brightness(1.05);
}

.error {
  color: var(--danger, #b00020);
}

.field-error {
  color: var(--danger, #b00020);
  font-size: 0.85rem;
}

.ok {
  color: var(--ok, #0a7a4b);
}
</style>
