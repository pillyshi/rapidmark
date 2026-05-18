<template>
  <aside class="sidebar">

    <!-- Classification mode: full-sidebar label picker -->
    <template v-if="isClassification">
      <div class="sidebar-section-head">Label</div>
      <div class="classification-picker">
        <button
          v-for="label in derivedLabels"
          :key="label.id"
          :class="['cls-btn', { selected: currentClassification === label.id }]"
          :style="clsButtonStyle(label.hue)"
          @click="onClassify(label.id)"
        >
          <span class="cls-dot" />
          <span class="cls-name">{{ label.name }}</span>
          <span class="cls-short">{{ label.short }}</span>
          <kbd v-if="label.key">{{ label.key }}</kbd>
          <span v-if="currentClassification === label.id" class="cls-check">✓</span>
        </button>
      </div>
    </template>

    <!-- NER mode: tabs + entity list -->
    <template v-else>
      <div class="tabs">
        <button
          :class="['tab', activeTab === 'entity' ? 'active' : '']"
          @click="activeTab = 'entity'"
        >
          Entity
          <span class="tab-count">{{ docEntities.length }}</span>
        </button>
        <button
          :class="['tab', activeTab === 'comment' ? 'active' : '']"
          @click="activeTab = 'comment'"
        >
          Comment
          <span class="tab-count muted">—</span>
        </button>
      </div>

      <template v-if="activeTab === 'entity'">
        <div v-if="docEntities.length === 0" class="empty">
          <div class="empty-icon" aria-hidden="true">┼</div>
          <p class="empty-title">No entities yet</p>
          <p class="empty-sub">Select text in the document to annotate it.</p>
        </div>

        <div v-else class="entity-list">
          <div
            v-for="entity in sortedEntities"
            :key="entity.id"
            :class="['ent-row', { selected: selectedEntityId === entity.id }]"
            @click="toggleEntitySelection(entity.id)"
          >
            <div class="ent-row-left">
              <span
                class="ent-row-dot"
                :style="{ background: dotColor(entity.labelId) }"
              />
              <div class="ent-row-text">
                <span class="ent-row-quote">{{ entity.quote }}</span>
                <span class="ent-row-meta">
                  <span
                    class="ent-row-label"
                    :style="{ color: dotColor(entity.labelId) }"
                  >{{ labelShort(entity.labelId) }}</span>
                  <span class="ent-row-range">{{ entity.start }}–{{ entity.end }}</span>
                </span>
              </div>
            </div>
            <button
              class="ent-row-del"
              @click.stop="removeEntity(entity.id)"
              aria-label="Delete"
              title="Delete"
            >×</button>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="empty">
          <div class="empty-icon" aria-hidden="true">◌</div>
          <p class="empty-title">Comments coming soon</p>
          <p class="empty-sub">A future version will support per-document notes.</p>
        </div>
      </template>
    </template>

  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTask } from '../composables/useTask'
import { useEntity } from '../composables/useEntity'
import { useEntitySelection } from '../composables/useEntitySelection'
import { useLabel } from '../composables/useLabel'
import { useClassification } from '../composables/useClassification'
import { getLabelColors } from '../utils/labelColors'

const { currentText, isClassification } = useTask()
const { currentClassification, setClassification, clearClassification } = useClassification()
const { derivedLabels, getLabelById } = useLabel()
const { entities, removeEntity } = useEntity()
const { selectedEntityId, toggleEntitySelection } = useEntitySelection()

const activeTab = ref<'entity' | 'comment'>('entity')

const docEntities = computed(() => {
  if (!currentText.value) return []
  return entities.value.filter(e => e.textId === currentText.value!.id)
})

const sortedEntities = computed(() =>
  [...docEntities.value].sort((a, b) => a.start - b.start)
)

const dotColor = (labelId: string): string => {
  const label = getLabelById(labelId)
  if (!label) return 'oklch(0.62 0.16 200)'
  return getLabelColors(label.hue, 'tinted').dot
}

const labelShort = (labelId: string): string => {
  const label = getLabelById(labelId)
  return label?.short || labelId
}

const labelName = (labelId: string): string => {
  const label = getLabelById(labelId)
  return label?.name || labelId
}

const clsButtonStyle = (hue: number) => {
  const c = getLabelColors(hue, 'tinted')
  return { '--ent-bg': c.bg, '--ent-bg-deep': c.bgDeep, '--ent-border': c.border, '--ent-dot': c.dot, '--ent-ink': c.ink }
}

const onClassify = (labelId: string) => {
  if (!currentText.value) return
  if (currentClassification.value === labelId) {
    clearClassification(currentText.value.id)
  } else {
    setClassification(currentText.value.id, labelId)
  }
}
</script>
