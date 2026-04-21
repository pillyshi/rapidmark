import { useTask } from './useTask'
import { useEntity } from './useEntity'
import { useStatus } from './useStatus'

export function useResult() {
  const { task } = useTask()
  const { addEntity } = useEntity()
  const { setStatus } = useStatus()

  const loadResult = (data: any): void => {
    const taskInfoData = data.taskInfo || data.task_info
    if (!taskInfoData || !data.results) return

    Object.entries(data.results).forEach(([textId, textResult]: [string, any]) => {
      const textIndex = task.value?.texts?.findIndex(t => t.id === textId)
      if (textIndex === undefined || textIndex < 0) return

      if (textResult.status) {
        setStatus(textIndex, textResult.status)
      }

      if (textResult.attributes) {
        const text = task.value?.texts?.[textIndex]
        if (text) {
          text.attributes = { ...text.attributes, ...textResult.attributes }
        }
      }

      if (textResult.entities && Array.isArray(textResult.entities)) {
        textResult.entities.forEach((entity: any) => {
          addEntity({
            id: entity.id,
            textId: textId,
            start: entity.start,
            end: entity.end,
            quote: entity.text,
            labelId: entity.label || entity.labelId || entity.label_id
          })
        })
      }
    })
  }

  return { loadResult }
}
