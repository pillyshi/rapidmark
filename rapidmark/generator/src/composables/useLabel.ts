import { computed } from 'vue'
import { useTask } from "./useTask"

export const useLabel = () => {
  const { task } = useTask()
  
  const rootLabels = computed(() => {
    if (!task.value?.definition?.labels) return []
    return task.value.definition.labels.filter(label => !label.parentId)
  })
  const getChildLabels = computed(() => (parentId: string) => {
    if (!task.value?.definition?.labels) return []
    return task.value.definition.labels.filter(label => label.parentId === parentId)
  })

  const getLabelName = computed(() => (labelId: string): string => {
    if (!labelId) return '[No Label]'
    if (!task.value?.definition?.labels) return labelId

    const label = task.value.definition.labels.find(l => l.id === labelId)
    return (label?.name && label.name.trim()) ? label.name : labelId
  })

  return {
    rootLabels,
    getChildLabels,
    getLabelName
  }
}
