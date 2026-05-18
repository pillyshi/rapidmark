<template>
  <aside class="sidebar">
    <!-- Tabs -->
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

    <!-- Entity tab -->
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

    <!-- Comment tab -->
    <template v-else>
      <div class="empty">
        <div class="empty-icon" aria-hidden="true">◌</div>
        <p class="empty-title">Comments coming soon</p>
        <p class="empty-sub">A future version will support per-document notes.</p>
      </div>
    </template>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTask } from '../composables/useTask'
import { useEntity } from '../composables/useEntity'
import { useEntitySelection } from '../composables/useEntitySelection'
import { useLabel } from '../composables/useLabel'
import { getLabelColors } from '../utils/labelColors'

const { currentText } = useTask()
const { entities, removeEntity } = useEntity()
const { selectedEntityId, toggleEntitySelection } = useEntitySelection()
const { getLabelById } = useLabel()

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
</script>
