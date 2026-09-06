const ALLOWED_TAGS = new Set(['a', 'code', 'i', 'strong'])
const SAFE_PROTOCOLS = new Set(['http:', 'https:', 'mailto:'])

/**
 * Same idea as backend TagBalanceParser: tags must nest and close correctly.
 * @returns {string|null} error message or null if ok
 */
export function validateTagBalance(html) {
  const stack = []
  const re = /<\/?([a-zA-Z0-9]+)(?:\s[^>]*)?\s*>/g
  let match

  while ((match = re.exec(html)) !== null) {
    const full = match[0]
    const tag = match[1].toLowerCase()

    if (full.startsWith('</')) {
      if (!stack.length || stack[stack.length - 1] !== tag) {
        return `Invalid or unclosed tag structure near </${tag}>`
      }
      stack.pop()
    } else {
      stack.push(tag)
    }
  }

  if (stack.length) {
    return `Unclosed tag(s): ${stack.join(', ')}`
  }
  return null
}

function isSafeHref(href) {
  if (!href) return false
  try {
    const url = new URL(href, 'https://example.invalid')
    return SAFE_PROTOCOLS.has(url.protocol)
  } catch {
    return false
  }
}

function sanitizeNode(node, doc) {
  if (node.nodeType === Node.TEXT_NODE) {
    return doc.createTextNode(node.textContent)
  }
  if (node.nodeType !== Node.ELEMENT_NODE) {
    return null
  }

  const tag = node.tagName.toLowerCase()

  if (!ALLOWED_TAGS.has(tag)) {
    const frag = doc.createDocumentFragment()
    for (const child of [...node.childNodes]) {
      const cleaned = sanitizeNode(child, doc)
      if (cleaned) frag.appendChild(cleaned)
    }
    return frag
  }

  const el = doc.createElement(tag)
  if (tag === 'a') {
    const href = node.getAttribute('href')
    const title = node.getAttribute('title')
    if (href && isSafeHref(href)) {
      el.setAttribute('href', href)
    }
    if (title) {
      el.setAttribute('title', title)
    }
  }

  for (const child of [...node.childNodes]) {
    const cleaned = sanitizeNode(child, doc)
    if (cleaned) el.appendChild(cleaned)
  }
  return el
}

/** Whitelist like backend bleach.clean; strips other tags. */
export function sanitizeCommentHtml(html) {
  const doc = new DOMParser().parseFromString(`<div>${html}</div>`, 'text/html')
  const wrapper = doc.body.firstElementChild
  if (!wrapper) return ''

  const out = doc.createElement('div')
  for (const child of [...wrapper.childNodes]) {
    const cleaned = sanitizeNode(child, doc)
    if (cleaned) out.appendChild(cleaned)
  }
  return out.innerHTML
}

/** Safe HTML for preview: balance check + sanitize. */
export function previewHtml(raw) {
  const text = raw?.trim() ? raw : ''
  if (!text) return '<em>Nothing to preview</em>'

  const balanceError = validateTagBalance(text)
  if (balanceError) {
    return `<span class="preview-error">${escapeText(balanceError)}</span>`
  }
  return sanitizeCommentHtml(text)
}

function escapeText(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
