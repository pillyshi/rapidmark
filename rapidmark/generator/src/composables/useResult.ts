import { useTask } from './useTask'
import { useEntity } from './useEntity'
import { useStatus } from './useStatus'

export function useResult() {
  const { task } = useTask()
  const { entities, addEntity } = useEntity()
  const { statuses, setStatus } = useStatus()

  const loadResult = (data: any): void => {
    // New format: { task, worker, texts: [{ id, status, entities }] }
    if (data.texts && Array.isArray(data.texts)) {
      data.texts.forEach((tx: any) => {
        const textIndex = task.value?.texts?.findIndex(t => t.id === tx.id)
        if (textIndex === undefined || textIndex < 0) return
        if (tx.status) setStatus(textIndex, tx.status)
        if (Array.isArray(tx.entities)) {
          tx.entities.forEach((en: any) => {
            if (typeof en.start === 'number' && typeof en.end === 'number' && (en.labelId || en.label)) {
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
    const payload = {
      task: { id: def?.id || '', name: def?.name || '', type: def?.type || 'ner' },
      worker: workerName || null,
      exported_at: new Date().toISOString(),
      texts: (task.value?.texts || []).map((txt, idx) => ({
        id: txt.id,
        status: statuses.value[idx] || 'pending',
        attributes: txt.attributes,
        entities: entities.value
          .filter(e => e.textId === txt.id)
          .map(e => ({ id: e.id, start: e.start, end: e.end, quote: e.quote, labelId: e.labelId }))
      }))
    }
    return JSON.stringify(payload, null, 2)
  }

  return { loadResult, exportResult }
}
