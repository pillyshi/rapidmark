import { ref } from 'vue'

const highlightedEntityId = ref<string | null>(null)

export const useEntityHighlight = () => {
  const setHighlightedEntity = (entityId: string | null) => {
    highlightedEntityId.value = entityId
  }

  const clearHighlight = () => {
    highlightedEntityId.value = null
  }

  const isEntityHighlighted = (entityId: string) => {
    return highlightedEntityId.value === entityId
  }

  return {
    highlightedEntityId,
    setHighlightedEntity,
    clearHighlight,
    isEntityHighlighted
  }
}