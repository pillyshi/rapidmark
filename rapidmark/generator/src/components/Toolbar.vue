<template>
  <div class="toolbar">
    <!-- Navigation cluster -->
    <div class="nav-cluster">
      <button class="icon-btn" :disabled="isFirst" @click="goPrev" aria-label="Previous">‹</button>
      <div class="doc-counter">
        <span class="doc-cur">{{ padded(docIdx + 1) }}</span>
        <span class="doc-slash">/</span>
        <span class="doc-tot">{{ padded(total) }}</span>
      </div>
      <button class="icon-btn" :disabled="isLast" @click="goNext" aria-label="Next">›</button>
      <button class="pill-btn" @click="goNextPending">
        Next pending <kbd>N</kbd>
      </button>
    </div>

    <!-- Status segmented control -->
    <div class="status-cluster">
      <span class="cluster-label">STATUS</span>
      <div class="status-segmented" :data-current="currentStatus">
        <button
          :class="['seg', currentStatus === 'pending' ? 'active' : '']"
          @click="setStatus('pending')"
        >
          <i class="pip pending" /> Pending
        </button>
        <button
          :class="['seg', currentStatus === 'completed' ? 'active' : '']"
          @click="setStatus(currentStatus === 'completed' ? 'pending' : 'completed')"
        >
          <i class="pip completed" /> Completed <kbd>C</kbd>
        </button>
        <button
          :class="['seg', currentStatus === 'excluded' ? 'active' : '']"
          @click="setStatus(currentStatus === 'excluded' ? 'pending' : 'excluded')"
        >
          <i class="pip excluded" /> Excluded <kbd>X</kbd>
        </button>
      </div>
    </div>

    <!-- Progress cluster -->
    <div class="progress-cluster">
      <div class="progress-numbers">
        <span class="progress-pct">{{ pct }}%</span>
        <span class="progress-frac">
          <b>{{ completedCount }}</b> / {{ total }}
          <em>Completed</em>
        </span>
        <span class="progress-excluded">
          <i class="pip excluded" /> {{ excludedCount }} Excluded
        </span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: pct + '%' }" />
        <div class="progress-excluded-fill" :style="{ width: excludedPct + '%' }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTask } from '../composables/useTask'
import { useStatus } from '../composables/useStatus'
import { useEntitySelection } from '../composables/useEntitySelection'
import { usePopover } from '../composables/usePopover'

const { task, currentTextIndex } = useTask()
const { statuses, currentStatus, setCurrentStatus } = useStatus()
const { clearEntitySelection } = useEntitySelection()
const { clearPopover } = usePopover()

const total = computed(() => task.value?.texts?.length || 0)
const docIdx = computed(() => currentTextIndex.value)
const isFirst = computed(() => docIdx.value <= 0)
const isLast = computed(() => docIdx.value >= total.value - 1)

const completedCount = computed(() => statuses.value.filter(s => s === 'completed').length)
const excludedCount = computed(() => statuses.value.filter(s => s === 'excluded').length)
const pct = computed(() => total.value === 0 ? 0 : Math.round((completedCount.value / total.value) * 100))
const excludedPct = computed(() => total.value === 0 ? 0 : Math.round((excludedCount.value / total.value) * 100))

const navigate = (newIdx: number) => {
  currentTextIndex.value = newIdx
  clearEntitySelection()
  clearPopover()
}

const goPrev = () => { if (!isFirst.value) navigate(docIdx.value - 1) }
const goNext = () => { if (!isLast.value) navigate(docIdx.value + 1) }

const goNextPending = () => {
  const n = total.value
  for (let k = 1; k <= n; k++) {
    const cand = (docIdx.value + k) % n
    if ((statuses.value[cand] || 'pending') === 'pending') {
      navigate(cand)
      return
    }
  }
}

const setStatus = (status: 'pending' | 'completed' | 'excluded') => {
  setCurrentStatus(status)
}

const padded = (n: number) => String(n).padStart(2, '0')

// Expose navigation for keyboard shortcuts
defineExpose({ goPrev, goNext, goNextPending, setStatus })
</script>
