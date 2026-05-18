import { ref, computed } from 'vue'

const selectedEntityIds = ref<string[]>([])

export const useEntitySelection = () => {
  const toggleEntitySelection = (id: string) => {
    selectedEntityIds.value = selectedEntityIds.value.includes(id)
      ? selectedEntityIds.value.filter(x => x !== id)
      : [...selectedEntityIds.value, id]
  }

  const selectEntity = (id: string) => {
    selectedEntityIds.value = [id]
  }

  const clearEntitySelection = () => {
    selectedEntityIds.value = []
  }

  const isEntitySelected = (id: string) => selectedEntityIds.value.includes(id)

  // backward compat: first selected entity or null
  const selectedEntityId = computed(() => selectedEntityIds.value[0] ?? null)

  return { selectedEntityIds, selectedEntityId, toggleEntitySelection, selectEntity, clearEntitySelection, isEntitySelected }
}
