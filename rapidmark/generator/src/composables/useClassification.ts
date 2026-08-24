import { ref, computed } from 'vue'
import { useTask } from './useTask'
import { useStatus } from './useStatus'

const classifications = ref<Record<string, string>>({})  // textId → labelId

export function useClassification() {
  const { task, currentText } = useTask()
  const { setStatus } = useStatus()

  const currentClassification = computed(() =>
    currentText.value ? classifications.value[currentText.value.id] ?? null : null
  )

  const setClassification = (textId: string, labelId: string) => {
    classifications.value = { ...classifications.value, [textId]: labelId }
    const textIndex = task.value?.texts?.findIndex(t => t.id === textId)
    if (textIndex !== undefined && textIndex >= 0) setStatus(textIndex, 'completed')
  }

  const clearClassification = (textId: string) => {
    const next = { ...classifications.value }
    delete next[textId]
    classifications.value = next
    const textIndex = task.value?.texts?.findIndex(t => t.id === textId)
    if (textIndex !== undefined && textIndex >= 0) setStatus(textIndex, 'pending')
  }

  return { classifications, currentClassification, setClassification, clearClassification }
}
