import { ref, computed } from "vue"
import { useTask } from "./useTask"

type Status = "pending" | "completed" | "excluded"

const statuses = ref<Status[]>([])

export const useStatus = () => {
  const { task, currentTextIndex } = useTask()
  
  const initializeStatuses = () => {
    if (task.value != null) {
      statuses.value = task.value.texts.map(() => "pending")
    }
  }
  
  const setStatus = (textIndex: number, status: Status) => {
    if (textIndex >= 0 && textIndex < statuses.value.length) {
      statuses.value = [
        ...statuses.value.slice(0, textIndex),
        status,
        ...statuses.value.slice(textIndex + 1)
      ]
      // statuses.value[textIndex] = status
      return true
    }
    return false
  }
  
  const setCurrentStatus = (status: Status) => {
    return setStatus(currentTextIndex.value, status)
  }
  
  const getStatus = (textIndex: number): Status | null => {
    if (textIndex >= 0 && textIndex < statuses.value.length) {
      return statuses.value[textIndex]
    }
    return null
  }
  
  const currentStatus = computed(() => {
    return getStatus(currentTextIndex.value)
  })
  
  const resetStatuses = () => {
    statuses.value = statuses.value.map(() => "pending")
  }
  
  // Initialize on first load
  if (task.value != null && statuses.value.length === 0) {
    initializeStatuses()
  }
  
  return {
    statuses,
    currentStatus,
    setStatus,
    setCurrentStatus,
    getStatus,
    initializeStatuses,
    resetStatuses
  }
}
