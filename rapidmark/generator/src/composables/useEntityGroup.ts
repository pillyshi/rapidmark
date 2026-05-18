import { ref, computed } from 'vue'
import { useTask } from './useTask'

interface EntityGroup {
  id: string
  textId: string
  entityIds: string[]
}

const groups = ref<EntityGroup[]>([])

export function useEntityGroup() {
  const { currentText } = useTask()

  const docGroups = computed(() =>
    groups.value.filter(g => g.textId === currentText.value?.id)
  )

  const createGroup = (textId: string, entityIds: string[]): string => {
    const id = 'g_' + Math.random().toString(36).slice(2, 9)
    groups.value = [...groups.value, { id, textId, entityIds }]
    return id
  }

  const deleteGroup = (groupId: string) => {
    groups.value = groups.value.filter(g => g.id !== groupId)
  }

  const cleanupEntity = (entityId: string) => {
    groups.value = groups.value
      .map(g => ({ ...g, entityIds: g.entityIds.filter(id => id !== entityId) }))
      .filter(g => g.entityIds.length >= 2)
  }

  return { groups, docGroups, createGroup, deleteGroup, cleanupEntity }
}
