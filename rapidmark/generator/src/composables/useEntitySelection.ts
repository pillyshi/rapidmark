import { ref } from 'vue'

const selectedEntityIds = ref<string[]>([])

export const useEntitySelection = () => {
  const toggleEntitySelection = (entityId: string) => {
    const idx = selectedEntityIds.value.indexOf(entityId)
    if (idx === -1) {
      selectedEntityIds.value.push(entityId)
    } else {
      selectedEntityIds.value.splice(idx, 1)
    }
  }

  const clearEntitySelection = () => {
    selectedEntityIds.value = []
  }

  const isEntitySelected = (entityId: string) =>
    selectedEntityIds.value.includes(entityId)

  return { selectedEntityIds, toggleEntitySelection, clearEntitySelection, isEntitySelected }
}
