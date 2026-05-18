import { ref, computed } from 'vue'
import { useTask } from './useTask'
import { useStatus } from './useStatus'

const classifications = ref<Record<string, string>>({})  // textId → labelId

export function useClassification() {
  const { currentText } = useTask()
  const { setCurrentStatus } = useStatus()

  const currentClassification = computed(() =>
    currentText.value ? classifications.value[currentText.value.id] ?? null : null
  )

  const setClassification = (textId: string, labelId: string) => {
    classifications.value = { ...classifications.value, [textId]: labelId }
    setCurrentStatus('completed')
  }

  const clearClassification = (textId: string) => {
    const next = { ...classifications.value }
    delete next[textId]
    classifications.value = next
    setCurrentStatus('pending')
  }

  return { classifications, currentClassification, setClassification, clearClassification }
}
