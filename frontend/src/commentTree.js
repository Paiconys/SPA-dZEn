/** Flatten nested API comments into a single list. */
export function flattenComments(nodes, out = []) {
  for (const node of nodes || []) {
    const { replies, ...rest } = node
    out.push(rest)
    if (replies?.length) {
      flattenComments(replies, out)
    }
  }
  return out
}

/**
 * Build a tree: only roots (parent == null) at top level;
 * replies hang under their parent via `replies`.
 */
export function buildCommentTree(results) {
  const flat = flattenComments(results)
  const map = new Map()

  for (const c of flat) {
    map.set(c.id, { ...c, replies: [] })
  }

  const roots = []
  const rootOrder = []

  for (const c of flat) {
    const node = map.get(c.id)
    // parent == null → root; self-parent is bad data → treat as root
    if (c.parent == null || c.parent === c.id) {
      roots.push(node)
      rootOrder.push(c.id)
    } else if (map.has(c.parent)) {
      map.get(c.parent).replies.push(node)
    }
    // reply whose parent is missing from this payload → skip from main table
  }

  function sortReplies(nodes) {
    nodes.sort(
      (a, b) => new Date(a.created_at) - new Date(b.created_at),
    )
    for (const n of nodes) {
      sortReplies(n.replies)
    }
  }

  for (const root of roots) {
    sortReplies(root.replies)
  }

  // Keep root order as returned by API (after filtering to roots)
  roots.sort(
    (a, b) => rootOrder.indexOf(a.id) - rootOrder.indexOf(b.id),
  )

  return roots
}
