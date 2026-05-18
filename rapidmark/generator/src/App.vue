<template>
  <div class="app" data-density="regular">
    <TopBar
      :task-name="task?.definition?.name || ''"
      :loading="loading"
      :worker="worker"
      @update:worker="worker = $event"
      @import="triggerImport"
      @export="handleExport"
    />

    <input
      ref="fileInputRef"
      type="file"
      accept="application/json,.json"
      style="display: none"
      @change="onFileSelected"
    />

    <Toolbar ref="toolbarRef" />

    <main class="main">
      <DocPanel ref="docPanelRef" />
      <Sidebar />
    </main>

    <!-- Error banner -->
    <div v-if="importError" class="banner error" role="alert">
      <span class="banner-icon">!</span>
      <span class="banner-msg">{{ importError }}</span>
      <button class="banner-x" @click="clearError">×</button>
    </div>

    <!-- Toast -->
    <div v-if="toast" class="banner toast" role="status">
      <span class="banner-icon">✓</span>
      <span class="banner-msg">{{ toast }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import TopBar from './components/TopBar.vue'
import Toolbar from './components/Toolbar.vue'
import DocPanel from './components/DocPanel.vue'
import Sidebar from './components/Sidebar.vue'
import { useTask } from './composables/useTask'
import { useStatus } from './composables/useStatus'
import { useEntity } from './composables/useEntity'
import { useEntitySelection } from './composables/useEntitySelection'
import { useLabel } from './composables/useLabel'
import { usePopover } from './composables/usePopover'
import { useToast } from './composables/useToast'
import { useResult } from './composables/useResult'

const { task, loadTask, currentTextIndex } = useTask()
const { initializeStatuses, statuses, currentStatus, setCurrentStatus } = useStatus()
const { entities, removeEntity } = useEntity()
const { selectedEntityId, clearEntitySelection } = useEntitySelection()
const { derivedLabels } = useLabel()
const { popover, clearPopover } = usePopover()
const { toast, importError, showToast, showError, clearError } = useToast()
const { loadResult, exportResult } = useResult()

declare const __RESULT_CONFIG__: any

const loading = ref(true)
const worker = ref((import.meta.env.RAPIDMARK_WORKER_NAME as string) || '')
const fileInputRef = ref<HTMLInputElement | null>(null)
const toolbarRef = ref<InstanceType<typeof Toolbar> | null>(null)
const docPanelRef = ref<InstanceType<typeof DocPanel> | null>(null)

onMounted(async () => {
  await loadTask()
  initializeStatuses()
  if (__RESULT_CONFIG__ !== null) {
    loadResult(__RESULT_CONFIG__)
  }
  // Fake shimmer: show loading for 850ms
  setTimeout(() => { loading.value = false }, 850)
})

// ── Import / Export ──────────────────────────────────────────────────────────
const triggerImport = () => { fileInputRef.value?.click() }

const handleExport = () => {
  const json = exportResult(worker.value)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  const taskId = task.value?.definition?.id || 'rapidmark'
  const safeWorker = (worker.value || '').replace(/[^a-z0-9_-]+/gi, '_')
  a.href = url
  a.download = safeWorker
    ? `${taskId}.${safeWorker}.result.rapidmark.json`
    : `${taskId}.result.rapidmark.json`
  a.click()
  URL.revokeObjectURL(url)
  showToast('Result file downloaded')
}

const onFileSelected = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result as string)
      if (!data || (!data.texts && !data.results)) {
        throw new Error('Invalid result file format (texts / results not found)')
      }
      loadResult(data)
      clearError()
      const n = entities.value.length
      showToast(`${n} entities restored`)
    } catch (err: any) {
      showError(err.message || 'Failed to parse JSON')
    }
    ;(e.target as HTMLInputElement).value = ''
  }
  reader.onerror = () => showError('Failed to read file')
  reader.readAsText(file)
}

// ── Keyboard shortcuts ───────────────────────────────────────────────────────
const goNext = () => {
  const max = (task.value?.texts?.length || 1) - 1
  if (currentTextIndex.value < max) {
    currentTextIndex.value++
    clearEntitySelection()
    clearPopover()
  }
}
const goPrev = () => {
  if (currentTextIndex.value > 0) {
    currentTextIndex.value--
    clearEntitySelection()
    clearPopover()
  }
}
const goNextPending = () => {
  const n = task.value?.texts?.length || 0
  for (let k = 1; k <= n; k++) {
    const cand = (currentTextIndex.value + k) % n
    if ((statuses.value[cand] || 'pending') === 'pending') {
      currentTextIndex.value = cand
      clearEntitySelection()
      clearPopover()
      return
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
})

const onKey = (e: KeyboardEvent) => {
  const target = e.target as HTMLElement
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return

  // When popover is open: label shortcuts and escape
  if (popover.value) {
    const lbl = derivedLabels.value.find(l => l.key === e.key)
    if (lbl) {
      e.preventDefault()
      docPanelRef.value?.createEntity(lbl.id)
      return
    }
    if (e.key === 'Escape') {
      e.preventDefault()
      docPanelRef.value?.cancelPopover()
      return
    }
  }

  if (e.key === 'j' || e.key === 'ArrowRight') { e.preventDefault(); goNext() }
  else if (e.key === 'k' || e.key === 'ArrowLeft') { e.preventDefault(); goPrev() }
  else if (e.key === 'n') { e.preventDefault(); goNextPending() }
  else if (e.key === 'c' && !e.metaKey && !e.ctrlKey) {
    e.preventDefault()
    setCurrentStatus(currentStatus.value === 'completed' ? 'pending' : 'completed')
  }
  else if (e.key === 'x') {
    e.preventDefault()
    setCurrentStatus(currentStatus.value === 'excluded' ? 'pending' : 'excluded')
  }
  else if (e.key === 'Delete' || e.key === 'Backspace') {
    if (selectedEntityId.value) {
      e.preventDefault()
      removeEntity(selectedEntityId.value)
      clearEntitySelection()
    }
  }
}
</script>
