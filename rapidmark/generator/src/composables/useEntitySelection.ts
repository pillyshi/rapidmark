import { ref } from 'vue'

const selectedEntityId = ref<string | null>(null)

export const useEntitySelection = () => {
  const selectEntity = (id: string | null) => {
    selectedEntityId.value = id
  }

  const toggleEntitySelection = (id: string) => {
    selectedEntityId.value = selectedEntityId.value === id ? null : id
  }

  const clearEntitySelection = () => {
    selectedEntityId.value = null
  }

  const isEntitySelected = (id: string) => selectedEntityId.value === id

  // backward compat
  const selectedEntityIds = { value: selectedEntityId.value ? [selectedEntityId.value] : [] }

  return { selectedEntityId, selectedEntityIds, selectEntity, toggleEntitySelection, clearEntitySelection, isEntitySelected }
}
