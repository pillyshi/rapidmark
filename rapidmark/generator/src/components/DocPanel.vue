<template>
  <section class="doc-panel">
    <!-- Doc header -->
    <div class="doc-header">
      <div class="doc-id-block">
        <span class="doc-id-kicker">DOC ID</span>
        <span class="doc-id">{{ currentText?.id }}</span>
        <span :class="['doc-status-tag', currentStatus || 'pending']">
          <i :class="['pip', currentStatus || 'pending']" />
          {{ statusLabel }}
        </span>
      </div>
      <div class="doc-attrs">
        <div v-for="(val, key) in currentText?.attributes" :key="key" class="attr">
          <span class="attr-k">{{ key }}</span>
          <span class="attr-v">{{ val }}</span>
        </div>
      </div>
    </div>

    <!-- Document text area -->
    <div class="doc-text-wrap">
      <div
        ref="textRef"
        class="doc-text"
        @mouseup="handleMouseUp"
        @mousedown="handleMouseDown"
      >
        <template v-for="(seg, i) in segments" :key="i">
          <span v-if="seg.kind === 'text'">{{ seg.text }}</span>
          <span
            v-else-if="seg.entity && seg.label"
            :class="['ent', { selected: selectedEntityId === seg.entity.id }, 'style-tinted']"
            :style="entStyle(seg.label.hue)"
            :title="`${seg.label.name} · ${seg.entity.start}–${seg.entity.end}`"
            @click.stop="toggleEntitySelection(seg.entity.id)"
          >
            <span class="ent-text">{{ seg.entity.quote }}</span>
            <span class="ent-tag">
              <span class="ent-dot" />
              {{ seg.label.short }}
            </span>
          </span>
          <span v-else>{{ seg.entity?.quote }}</span>
        </template>

        <!-- Label selection popover -->
        <div
          v-if="popover"
          ref="popoverRef"
          class="popover"
          :style="{ left: popover.x + 'px', top: popover.y + 'px' }"
          @mousedown.stop
        >
          <div class="popover-head">
            <div class="popover-sel">
              <span class="popover-quote">「{{ truncate(popover.quote, 28) }}」</span>
              <span class="popover-range">[{{ popover.start }}, {{ popover.end }}] · {{ popover.end - popover.start }} chars</span>
            </div>
            <button class="popover-x" @click="cancelPopover" aria-label="Close">×</button>
          </div>

          <div v-if="derivedLabels.length === 0" class="popover-empty">
            No labels defined in this task
          </div>
          <div v-else class="popover-groups">
            <div v-for="group in labelGroups" :key="group.name" class="popover-group">
              <div class="popover-group-name">{{ group.name }}</div>
              <div class="popover-items">
                <button
                  v-for="label in group.labels"
                  :key="label.id"
                  class="popover-item"
                  :style="popoverItemStyle(label.hue)"
                  @click="createEntity(label.id)"
                >
                  <span class="popover-dot" />
                  <span class="popover-name">{{ label.name }}</span>
                  <span class="popover-short">{{ label.short }}</span>
                  <kbd v-if="label.key">{{ label.key }}</kbd>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Shortcut bar -->
    <div class="shortcuts">
      <span class="sc-group"><kbd>J</kbd><kbd>K</kbd>&nbsp;navigate</span>
      <span class="sc-group"><kbd>N</kbd>&nbsp;next pending</span>
      <span class="sc-group"><kbd>C</kbd>&nbsp;toggle done</span>
      <span class="sc-group"><kbd>X</kbd>&nbsp;toggle exclude</span>
      <span class="sc-group"><kbd>1</kbd>–<kbd>9</kbd>&nbsp;assign label</span>
      <span class="sc-group"><kbd>⌫</kbd>&nbsp;delete entity</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { useTask } from '../composables/useTask'
import { useEntity } from '../composables/useEntity'
import { useEntitySelection } from '../composables/useEntitySelection'
import { useStatus } from '../composables/useStatus'
import { useLabel } from '../composables/useLabel'
import { usePopover } from '../composables/usePopover'
import { useToast } from '../composables/useToast'
import { getLabelColors } from '../utils/labelColors'

const { currentText } = useTask()
const { entities, addEntity } = useEntity()
const { selectedEntityId, toggleEntitySelection, selectEntity } = useEntitySelection()
const { currentStatus } = useStatus()
const { derivedLabels, labelGroups, getLabelById } = useLabel()
const { popover, setPopover } = usePopover()
const { showToast } = useToast()

const textRef = ref<HTMLElement | null>(null)
const popoverRef = ref<HTMLElement | null>(null)

const statusLabel = computed(() => {
  const map: Record<string, string> = { pending: 'Pending', completed: 'Completed', excluded: 'Excluded' }
  return map[currentStatus.value || 'pending'] || 'Pending'
})

const docEntities = computed(() => {
  if (!currentText.value) return []
  return entities.value.filter(e => e.textId === currentText.value!.id)
})

interface TextSeg {
  kind: 'text'
  text: string
}
interface EntitySeg {
  kind: 'entity'
  entity: { id: string; quote: string; start: number; end: number; labelId: string }
  label: ReturnType<typeof getLabelById> | undefined
  text: string
}
type Segment = TextSeg | EntitySeg

const segments = computed((): Segment[] => {
  const content = currentText.value?.content
  if (!content) return []
  const sorted = [...docEntities.value].sort((a, b) => a.start - b.start)
  const out: Segment[] = []
  let cur = 0
  for (const e of sorted) {
    if (e.start > cur) out.push({ kind: 'text', text: content.slice(cur, e.start) })
    out.push({
      kind: 'entity',
      entity: e,
      label: getLabelById(e.labelId),
      text: content.slice(e.start, e.end),
    })
    cur = e.end
  }
  if (cur < content.length) out.push({ kind: 'text', text: content.slice(cur) })
  return out
})

const entStyle = (hue: number) => {
  const c = getLabelColors(hue, 'tinted')
  return {
    '--ent-bg': c.bg,
    '--ent-bg-deep': c.bgDeep,
    '--ent-border': c.border,
    '--ent-dot': c.dot,
    '--ent-ink': c.ink,
  }
}

const popoverItemStyle = (hue: number) => {
  const c = getLabelColors(hue, 'tinted')
  return { '--ent-bg': c.bg, '--ent-border': c.border, '--ent-dot': c.dot }
}

const truncate = (s: string, max: number) =>
  s.length > max ? s.slice(0, max - 2) + '…' : s

// ── Text offset calculation ──────────────────────────────────────────────────
// Skips .ent-tag elements (label chips) since their text is not part of the
// document content and would corrupt the offset if counted.
const offsetOf = (root: HTMLElement, node: Node, offset: number): number => {
  let n = 0
  const walk = (el: Node): boolean => {
    for (const child of el.childNodes) {
      if (child === node) { n += offset; return true }
      if (child.nodeType === Node.TEXT_NODE) {
        n += (child as Text).nodeValue!.length
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        if ((child as HTMLElement).classList?.contains('ent-tag')) continue
        if (walk(child)) return true
      }
    }
    return false
  }
  walk(root)
  return n
}

// ── Selection → popover ──────────────────────────────────────────────────────
const handleMouseUp = () => {
  const sel = window.getSelection()
  if (!sel || sel.isCollapsed) { setPopover(null); return }
  const range = sel.getRangeAt(0)
  const root = textRef.value
  if (!root || !root.contains(range.startContainer) || !root.contains(range.endContainer)) {
    setPopover(null); return
  }
  let start = offsetOf(root, range.startContainer, range.startOffset)
  let end = offsetOf(root, range.endContainer, range.endOffset)
  if (end < start) [start, end] = [end, start]
  if (end === start) { setPopover(null); return }
  const content = currentText.value?.content || ''
  const quote = content.slice(start, end)
  if (!quote.trim()) { setPopover(null); return }
  // Reject overlapping entities
  const overlap = docEntities.value.some(en => !(en.end <= start || en.start >= end))
  if (overlap) {
    sel.removeAllRanges()
    setPopover(null)
    showToast('Selection overlaps an existing entity')
    return
  }
  const rect = range.getBoundingClientRect()
  const hostRect = root.getBoundingClientRect()
  setPopover({
    start, end, quote,
    x: rect.left + rect.width / 2 - hostRect.left,
    y: rect.bottom - hostRect.top + 6,
  })
  // Clamp popover within the scrollable container on both sides
  nextTick(() => {
    const el = popoverRef.value
    if (!el) return
    el.style.transform = ''   // reset any previous clamp
    const container = el.closest('.doc-text-wrap') as HTMLElement
    if (!container) return
    const MARGIN = 8
    const w = el.offsetWidth
    const elRect = el.getBoundingClientRect()
    const cRect = container.getBoundingClientRect()
    const leftEdge = elRect.left - cRect.left
    const rightEdge = leftEdge + w
    if (leftEdge < MARGIN) {
      el.style.transform = `translateX(calc(-50% + ${MARGIN - leftEdge}px))`
    } else if (rightEdge > container.clientWidth - MARGIN) {
      el.style.transform = `translateX(calc(-50% - ${rightEdge - container.clientWidth + MARGIN}px))`
    }
  })
}

const handleMouseDown = () => {
  setPopover(null)
}

const cancelPopover = () => {
  setPopover(null)
  window.getSelection()?.removeAllRanges()
}

const createEntity = (labelId: string) => {
  if (!popover.value || !currentText.value) return
  const id = 'e_' + Math.random().toString(36).slice(2, 9)
  addEntity({
    id,
    textId: currentText.value.id,
    start: popover.value.start,
    end: popover.value.end,
    quote: popover.value.quote,
    labelId,
  })
  selectEntity(id)
  cancelPopover()
}

// Expose for keyboard shortcuts in App.vue
defineExpose({ cancelPopover, createEntity })
</script>
