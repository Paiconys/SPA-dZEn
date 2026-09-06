/** Turn absolute API media URLs into same-origin paths for the Vite proxy. */
export function toPublicUrl(url) {
  if (!url) return ''
  if (url.startsWith('/')) return url
  try {
    const parsed = new URL(url)
    return `${parsed.pathname}${parsed.search}`
  } catch {
    return url
  }
}
