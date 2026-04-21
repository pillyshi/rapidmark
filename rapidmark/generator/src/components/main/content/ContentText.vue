<template>
  <div style="height: 100%;">
    <v-card style="height: 100%;">
      <v-card-text style="height: 100%; padding: 0;">
        <div
          ref="textContainer"
          @mouseup="handleTextSelection"
          @click="handleClick"
          class="text-content"
          :style="{
            userSelect: 'text',
            cursor: 'text',
            height: '100%',
            whiteSpace: 'pre-wrap',
            fontFamily: 'Consolas, Monaco, Courier New, monospace',
            lineHeight: '1.5',
            padding: '16px',
            overflowY: 'auto',
            wordBreak: 'break-word'
          }"
          v-html="highlightedContent"
        />
      </v-card-text>
    </v-card>
    
    <SelectionOverlay 
      v-if="showOverlay"
      :selection="selectionData"
      @close="closeOverlay"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useTask } from '../../../composables/useTask'
import { useEntity } from '../../../composables/useEntity'
import { useEntityHighlight } from '../../../composables/useEntityHighlight'
import { useEntitySelection } from '../../../composables/useEntitySelection'
import { useLabel } from '../../../composables/useLabel'
import { getLabelBackgroundColor } from '../../../utils/labelColors'
import SelectionOverlay from './content-text/SelectionOverlay.vue'

const { task, currentText, loadTask } = useTask()
const { entities } = useEntity()
const { isEntityHighlighted } = useEntityHighlight()
const { isEntitySelected, toggleEntitySelection } = useEntitySelection()
const { rootLabels } = useLabel()

const textContainer = ref<HTMLElement | null>(null)
const showOverlay = ref(false)
const selectionData = ref<{
  text: string
  start: number
  end: number
  textId: string
  position: {
    x: number
    y: number
  }
} | null>(null)

const currentContent = computed(() => {
  return currentText.value?.content
})

const currentTextEntities = computed(() => {
  if (!currentText.value) return []
  return entities.value.filter(entity => entity.textId === currentText.value?.id)
})

const escapeHtml = (text: string): string =>
  text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')

const highlightedContent = computed(() => {
  const content = currentContent.value
  if (!content) return 'Loading...'

  const entities = currentTextEntities.value
  if (entities.length === 0) return escapeHtml(content)

  const sortedEntities = [...entities].sort((a, b) => a.start - b.start)

  let result = ''
  let lastIndex = 0

  sortedEntities.forEach(entity => {
    result += escapeHtml(content.substring(lastIndex, entity.start))

    const entityText = content.substring(entity.start, entity.end)
    const backgroundColor = getLabelBackgroundColor(entity.labelId, rootLabels.value)
    const isHighlighted = isEntityHighlighted(entity.id)
    const isSelected = isEntitySelected(entity.id)
    const highlightStyle = isHighlighted
      ? 'text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 2px; box-shadow: 0 0 8px rgba(255,255,255,0.6);'
      : ''
    const selectedStyle = isSelected
      ? 'text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 2px;'
      : ''

    result += `<span data-entity-id="${entity.id}" style="background-color: ${backgroundColor} !important; color: white !important; padding: 2px 4px; border-radius: 3px; font-weight: 500; display: inline; ${highlightStyle}${selectedStyle}" title="Label: ${entity.labelId}">${escapeHtml(entityText)}</span>`

    lastIndex = entity.end
  })

  result += escapeHtml(content.substring(lastIndex))
  return result
})

const calculateTextOffset = (containerElement: HTMLElement, range: Range): { start: number; end: number } | null => {
  try {
    // Walk only text nodes
    const walker = document.createTreeWalker(
      containerElement,
      NodeFilter.SHOW_TEXT,
      null,
      false
    )

    let currentOffset = 0
    let node: Text | null = null
    let startOffset = 0

    // Find selection start position
    while (node = walker.nextNode() as Text) {
      if (node === range.startContainer) {
        startOffset = currentOffset + range.startOffset
        break
      }
      currentOffset += node.textContent?.length || 0
    }

    const selectedText = range.toString()
    const endOffset = startOffset + selectedText.length

    return { start: startOffset, end: endOffset }
  } catch (error) {
    console.error('Error in TreeWalker text offset calculation:', error)
    return null
  }
}

const getPlainTextFromRange = (range: Range): string => {
  const contents = range.cloneContents()
  const tempDiv = document.createElement('div')
  tempDiv.appendChild(contents)

  // Extract plain text by stripping HTML tags
  return tempDiv.textContent || tempDiv.innerText || ''
}

const fallbackPositionCalculation = (textContent: string, selectedText: string): { start: number; end: number } => {
  const beforeSelection = textContent.substring(0, textContent.indexOf(selectedText))
  const start = beforeSelection.length
  const end = start + selectedText.length
  return { start, end }
}

const handleClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  const entityId = target.dataset?.entityId
  if (entityId) {
    toggleEntitySelection(entityId)
    window.getSelection()?.removeAllRanges()
  }
}

const handleTextSelection = () => {
  const selection = window.getSelection()

  if (selection && selection.toString().trim() && textContainer.value && currentText.value) {
    const selectedText = selection.toString()
    const range = selection.getRangeAt(0)

    // Get the position of the selection for overlay
    const rect = range.getBoundingClientRect()

    // Calculate accurate text positions using Range API
    let textPosition = null

    if (textContainer.value) {
      textPosition = calculateTextOffset(textContainer.value, range)
    }

    // Fallback to old method if Range API fails
    if (!textPosition) {
      console.warn('Range API position calculation failed, using fallback method')
      const textContent = currentContent.value || ''
      textPosition = fallbackPositionCalculation(textContent, selectedText)
    }

    const { start, end } = textPosition

    selectionData.value = {
      text: selectedText,
      start: start,
      end: end,
      textId: currentText.value.id,
      position: {
        x: rect.left + rect.width / 2,
        y: rect.bottom + 10
      }
    }

    showOverlay.value = true
  } else {
    showOverlay.value = false
  }
}

const closeOverlay = () => {
  showOverlay.value = false
  selectionData.value = null
  
  // Clear the text selection
  if (window.getSelection) {
    window.getSelection()?.removeAllRanges()
  }
}

onMounted(() => {
  loadTask()
})
</script>

<style scoped>
.text-content {
  user-select: text !important;
  cursor: text !important;
  height: 100% !important;
  white-space: pre-wrap !important;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  line-height: 1.5 !important;
  padding: 16px !important;
  overflow-y: auto !important;
  word-break: break-word;
}

.text-content :deep(.annotation) {
  white-space: pre-wrap;
}

.text-content :deep([data-entity-id]) {
  cursor: pointer;
}
</style>
