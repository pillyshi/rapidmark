<template>
  <div
    ref="overlayElement"
    class="selection-overlay"
    :style="overlayStyle"
  >
    <v-card class="overlay-card" elevation="8">
      <v-card-title>{{ selection?.text }} ({{ selection?.start }} - {{ selection?.end }})</v-card-title>
      <v-card-text>
        <div v-if="rootLabels.length > 0">
          <p><strong>Select label:</strong></p>
          <v-chip-group v-model="selectedLabelId" mandatory>
            <v-chip
              v-for="label in rootLabels"
              :key="label.id"
              :value="label.id"
              :style="{ backgroundColor: getLabelBackgroundColor(label.id, rootLabels), color: 'white' }"
              filter
              variant="flat"
            >
              {{ label.name }}
            </v-chip>
          </v-chip-group>
        </div>
        <div v-else>
          <p>No labels available</p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn 
          color="primary" 
          @click="createEntity"
          :disabled="!selectedLabelId"
        >
          Create Entity
        </v-btn>
        <v-btn @click="$emit('close')">Close</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useLabel } from '../../../../composables/useLabel'
import { useEntity } from '../../../../composables/useEntity'
import { getLabelBackgroundColor } from '@/utils/labelColors'

interface SelectionData {
  text: string
  start: number
  end: number
  textId: string
  position?: {
    x: number
    y: number
  }
}

interface Props {
  selection: SelectionData | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const { rootLabels } = useLabel()
const { addEntity } = useEntity()
const selectedLabelId = ref<string | null>(null)
const overlayElement = ref<HTMLElement | null>(null)

const calculateOptimalPosition = () => {
  if (!props.selection?.position || !overlayElement.value) {
    return {
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      zIndex: 1000
    }
  }

  const { x, y } = props.selection.position
  const rect = overlayElement.value.getBoundingClientRect()
  const cardWidth = rect.width || 350
  const cardHeight = rect.height || 200

  const margin = 10
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  const scrollY = window.scrollY
  const scrollX = window.scrollX

  // Smart positioning logic
  let finalX = x
  let finalY = y
  let transformX = '-50%'
  let transformY = '0'

  // Horizontal positioning
  const halfWidth = cardWidth / 2

  if (x - halfWidth < margin) {
    // Too close to left edge
    finalX = margin + halfWidth
    transformX = '-50%'
  } else if (x + halfWidth > viewportWidth - margin) {
    // Too close to right edge
    finalX = viewportWidth - margin - halfWidth
    transformX = '-50%'
  } else {
    // Can be centered
    finalX = x
    transformX = '-50%'
  }

  // Vertical positioning with priority
  const spaceBelow = viewportHeight - y
  const spaceAbove = y

  if (spaceBelow >= cardHeight + margin) {
    // Preferred: below the selection
    finalY = y + margin
    transformY = '0'
  } else if (spaceAbove >= cardHeight + margin) {
    // Alternative: above the selection
    finalY = y - margin
    transformY = '-100%'
  } else {
    // Last resort: center vertically with scroll adjustment
    finalY = Math.max(margin, Math.min(y, viewportHeight - cardHeight - margin))
    transformY = '0'
  }

  return {
    position: 'fixed',
    left: `${finalX}px`,
    top: `${finalY}px`,
    transform: `translate(${transformX}, ${transformY})`,
    zIndex: 1000,
    maxWidth: `${Math.min(400, viewportWidth - 2 * margin)}px`
  }
}

const overlayStyle = ref(calculateOptimalPosition())

// Recalculate position when selection changes or overlay is mounted
watch(() => props.selection, async () => {
  if (props.selection?.position) {
    await nextTick()
    overlayStyle.value = calculateOptimalPosition()
  }
}, { immediate: true })

onMounted(async () => {
  await nextTick()
  overlayStyle.value = calculateOptimalPosition()
})

const createEntity = () => {
  if (selectedLabelId.value && props.selection) {
    const selectedLabel = rootLabels.value.find(label => label.id === selectedLabelId.value)
    
    // Create entity using useEntity composable
    const newEntity = addEntity({
      textId: props.selection.textId,
      start: props.selection.start,
      end: props.selection.end,
      quote: props.selection.text,
      labelId: selectedLabelId.value
    })
    
    emit('close')
  }
}
</script>

<style scoped>
.selection-overlay {
  pointer-events: auto;
}

.overlay-card {
  min-width: 300px;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 80vh;
  overflow-y: auto;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .overlay-card {
    min-width: 280px;
    max-width: 90vw;
  }
}
</style>
