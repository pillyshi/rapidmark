import { useTask } from './useTask'
import { useEntity } from './useEntity'
import { useStatus } from './useStatus'
import { useClassification } from './useClassification'
import { useEntityGroup } from './useEntityGroup'

export function useResult() {
  const { task } = useTask()
  const { entities, addEntity } = useEntity()
  const { statuses, setStatus } = useStatus()
  const { classifications, setClassification } = useClassification()
  const { groups, createGroup } = useEntityGroup()

  const loadResult = (data: any): void => {
    // New format: { task, worker, texts: [{ id, status, entities }] }
    if (data.texts && Array.isArray(data.texts)) {
      data.texts.forEach((tx: any) => {
        const textIndex = task.value?.texts?.findIndex(t => t.id === tx.id)
        if (textIndex === undefined || textIndex < 0) return
        if (tx.status) setStatus(textIndex, tx.status)
        if (tx.label_id) setClassification(tx.id, tx.label_id)
        if (Array.isArray(tx.groups)) {
          tx.groups.forEach((g: any) => {
            const ids = g.entity_ids || g.entityIds || []
            if (ids.length >= 2) createGroup(tx.id, ids)
          })
        }
        if (Array.isArray(tx.entities)) {
          tx.entities.forEach((en: any) => {
            if (typeof en.start === 'number' && typeof en.end === 'number' && (en.labelId || en.label || en.label_id)) {
              addEntity({
                id: en.id,
                textId: tx.id,
                start: en.start,
                end: en.end,
                quote: en.quote || en.text || '',
                labelId: en.labelId || en.label || en.label_id || ''
              })
            }
          })
        }
      })
      return
    }

    // Legacy format: { taskInfo, results: { textId: { status, entities } } }
    if (data.results) {
      Object.entries(data.results).forEach(([textId, textResult]: [string, any]) => {
        const textIndex = task.value?.texts?.findIndex(t => t.id === textId)
        if (textIndex === undefined || textIndex < 0) return
        if (textResult.status) setStatus(textIndex, textResult.status)
        if (Array.isArray(textResult.entities)) {
          textResult.entities.forEach((en: any) => {
            addEntity({
              id: en.id,
              textId,
              start: en.start,
              end: en.end,
              quote: en.text || en.quote || '',
              labelId: en.label || en.labelId || en.label_id || ''
            })
          })
        }
      })
    }
  }

  const exportResult = (workerName: string): string => {
    const def = task.value?.definition
    const isClassification = def?.type === 'classification'
    const payload = {
      task_id: def?.id || '',
      result_version: 1,
      worker: workerName || null,
      exported_at: new Date().toISOString(),
      texts: (task.value?.texts || []).map((txt, idx) => {
        const base = {
          id: txt.id,
          status: statuses.value[idx] || 'pending',
        }
        if (isClassification) {
          return { ...base, label_id: classifications.value[txt.id] ?? null }
        }
        return {
          ...base,
          entities: entities.value
            .filter(e => e.textId === txt.id)
            .map(e => ({ id: e.id, start: e.start, end: e.end, quote: e.quote, label_id: e.labelId })),
          groups: groups.value
            .filter(g => g.textId === txt.id)
            .map(g => ({ id: g.id, entity_ids: g.entityIds }))
        }
      })
    }
    return JSON.stringify(payload, null, 2)
  }

  return { loadResult, exportResult }
}
