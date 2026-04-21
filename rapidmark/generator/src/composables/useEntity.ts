import { ref } from "vue";
import { Field } from "./useTask";


interface Entity {
  id: string
  textId: string
  start: number
  end: number
  quote: string
  labelId: string
}


const entities = ref<Entity[]>([])


export const useEntity = () => {
  const addEntity = (entityData: Omit<Entity, 'id'> & { id?: string }) => {
    const entity: Entity = {
      ...entityData,
      id: entityData.id || `entity_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
    entities.value.push(entity)
    return entity
  }
  
  const removeEntity = (entityId: string) => {
    const index = entities.value.findIndex(entity => entity.id === entityId)
    if (index !== -1) {
      entities.value.splice(index, 1)
      return true
    }
    return false
  }

  const getEntitiesByField = (field: Field) => {
    switch (field.kind) {
      case "full":
        return entities.value.filter((entity) => field.labelIds.includes(entity.labelId))
      case "withoutLabelIds":
        return []
      case "withoutStructureIds":
        return entities.value.filter((entity) => field.labelIds.includes(entity.labelId))
      case "groupOnly":
        return []
    }
  }
  
  return {
    entities,
    addEntity,
    removeEntity,
    getEntitiesByField
  }
}
