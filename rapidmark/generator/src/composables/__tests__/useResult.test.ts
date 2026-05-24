import { describe, expect, it, vi, beforeEach } from 'vitest'
import Ajv from 'ajv'
import addFormats from 'ajv-formats'
import mockNerTask from '../../__mocks__/task'
import mockClassificationTask from '../../__mocks__/classificationTask'
import resultSchema from '@schema/result.schema.json'

// All composables use module-level singleton refs.
// vi.resetModules() in beforeEach gives each test a fresh state.
const setup = async (mockTask: any) => {
  vi.stubGlobal('__TASK_CONFIG__', mockTask)
  const { useTask } = await import('../useTask')
  const { loadTask } = useTask()
  await loadTask()
  const { useResult } = await import('../useResult')
  return useResult()
}

describe('useResult', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  describe('exportResult — NER', () => {
    it('produces canonical v1 shape', async () => {
      const { exportResult } = await setup(mockNerTask)
      const data = JSON.parse(exportResult('alice'))

      expect(data.task_id).toBe('test_task')
      expect(data.result_version).toBe(1)
      expect(data.worker).toBe('alice')
      expect(typeof data.exported_at).toBe('string')
      expect(Array.isArray(data.texts)).toBe(true)
      expect(data.texts).toHaveLength(mockNerTask.texts.length)
    })

    it('does not contain forbidden top-level keys', async () => {
      const { exportResult } = await setup(mockNerTask)
      const data = JSON.parse(exportResult(''))

      expect(data).not.toHaveProperty('task')
      expect(data).not.toHaveProperty('taskInfo')
      expect(data).not.toHaveProperty('rapidmark_version')
    })

    it('exports entity label as label_id, not labelId', async () => {
      const { exportResult, loadResult } = await setup(mockNerTask)

      loadResult({
        texts: [{
          id: 'text_1',
          status: 'completed',
          entities: [{ id: 'e1', start: 0, end: 5, quote: 'Apple', label_id: 'organization' }]
        }]
      })

      const data = JSON.parse(exportResult(''))
      const t = data.texts.find((t: any) => t.id === 'text_1')
      expect(t.entities[0]).toHaveProperty('label_id')
      expect(t.entities[0]).not.toHaveProperty('labelId')
    })

    it('does not export texts[].attributes', async () => {
      const { exportResult } = await setup(mockNerTask)
      const data = JSON.parse(exportResult(''))

      data.texts.forEach((t: any) => {
        expect(t).not.toHaveProperty('attributes')
      })
    })
  })

  describe('exportResult — classification', () => {
    it('produces canonical v1 shape with per-text label_id', async () => {
      const { exportResult, loadResult } = await setup(mockClassificationTask)

      loadResult({
        texts: [
          { id: 'text_1', status: 'completed', label_id: 'pos' },
          { id: 'text_2', status: 'completed', label_id: 'neg' },
        ]
      })

      const data = JSON.parse(exportResult('bob'))
      expect(data.task_id).toBe('cls_task')
      expect(data.result_version).toBe(1)

      const t1 = data.texts.find((t: any) => t.id === 'text_1')
      expect(t1.label_id).toBe('pos')
      expect(t1).not.toHaveProperty('entities')
      expect(t1).not.toHaveProperty('attributes')
    })
  })

  describe('loadResult — backward compat', () => {
    it('imports v1 canonical format with snake_case label_id on entities', async () => {
      const { exportResult, loadResult } = await setup(mockNerTask)

      loadResult({
        task_id: 'test_task',
        result_version: 1,
        worker: 'alice',
        exported_at: '2026-01-01T00:00:00.000Z',
        texts: [{
          id: 'text_1',
          status: 'completed',
          entities: [{ id: 'e1', start: 0, end: 5, quote: 'Apple', label_id: 'organization' }],
          groups: []
        }]
      })

      const data = JSON.parse(exportResult(''))
      const t = data.texts.find((t: any) => t.id === 'text_1')
      expect(t.status).toBe('completed')
      expect(t.entities).toHaveLength(1)
      expect(t.entities[0].label_id).toBe('organization')
    })

    it('imports old format { task, worker, texts } with camelCase labelId', async () => {
      const { exportResult, loadResult } = await setup(mockNerTask)

      loadResult({
        task: { id: 'test_task', name: 'Test NER Task', type: 'ner' },
        worker: 'alice',
        exported_at: '2025-01-01T00:00:00.000Z',
        texts: [{
          id: 'text_1',
          status: 'completed',
          attributes: { source: 'tech_news' },
          entities: [{ id: 'e1', start: 0, end: 5, quote: 'Apple', labelId: 'organization' }],
          groups: []
        }]
      })

      const data = JSON.parse(exportResult(''))
      const t = data.texts.find((t: any) => t.id === 'text_1')
      expect(t.status).toBe('completed')
      expect(t.entities).toHaveLength(1)
      expect(t.entities[0].label_id).toBe('organization')
    })

    it('imports legacy format { taskInfo, results } with label key', async () => {
      const { exportResult, loadResult } = await setup(mockNerTask)

      loadResult({
        taskInfo: { taskId: 'test_task', taskType: 'ner' },
        results: {
          text_1: {
            status: 'completed',
            attributes: {},
            entities: [{ id: 'e1', start: 0, end: 5, text: 'Apple', label: 'organization' }]
          }
        }
      })

      const data = JSON.parse(exportResult(''))
      const t = data.texts.find((t: any) => t.id === 'text_1')
      expect(t.status).toBe('completed')
      expect(t.entities).toHaveLength(1)
      expect(t.entities[0].label_id).toBe('organization')
    })

    it('throws when task_id does not match the active task', async () => {
      const { loadResult } = await setup(mockNerTask)

      expect(() => loadResult({
        task_id: 'other_task',
        result_version: 1,
        worker: null,
        exported_at: '2026-01-01T00:00:00.000Z',
        texts: []
      })).toThrow(/other_task/)
    })

    it('error message contains both expected and actual task_id', async () => {
      const { loadResult } = await setup(mockNerTask)

      expect(() => loadResult({
        task_id: 'wrong_task',
        result_version: 1,
        worker: null,
        exported_at: '2026-01-01T00:00:00.000Z',
        texts: []
      })).toThrow(/test_task/)
    })

    it('succeeds when task_id matches the active task', async () => {
      const { loadResult } = await setup(mockNerTask)

      expect(() => loadResult({
        task_id: 'test_task',
        result_version: 1,
        worker: null,
        exported_at: '2026-01-01T00:00:00.000Z',
        texts: []
      })).not.toThrow()
    })

    it('skips task_id check for legacy files without task_id', async () => {
      const { loadResult } = await setup(mockNerTask)

      expect(() => loadResult({
        taskInfo: { taskId: 'other_task', taskType: 'ner' },
        results: {}
      })).not.toThrow()
    })

    it('ignores texts[].attributes in old-format files and still restores entities', async () => {
      const { exportResult, loadResult } = await setup(mockNerTask)

      loadResult({
        texts: [{
          id: 'text_2',
          status: 'excluded',
          attributes: { source: 'business_news' },
          entities: [{ id: 'e2', start: 0, end: 9, quote: 'Microsoft', label_id: 'organization' }],
          groups: []
        }]
      })

      const data = JSON.parse(exportResult(''))
      const t = data.texts.find((t: any) => t.id === 'text_2')
      expect(t.status).toBe('excluded')
      expect(t.entities).toHaveLength(1)
      expect(t).not.toHaveProperty('attributes')
    })
  })

  describe('schema conformance (ajv)', () => {
    let validate: ReturnType<Ajv['compile']>

    beforeEach(() => {
      const ajv = new Ajv()
      addFormats(ajv)
      validate = ajv.compile(resultSchema)
    })

    it('NER export conforms to result.schema.json', async () => {
      const { exportResult } = await setup(mockNerTask)
      const data = JSON.parse(exportResult('alice'))
      const valid = validate(data)
      if (!valid) console.error(validate.errors)
      expect(valid).toBe(true)
    })

    it('classification export conforms to result.schema.json', async () => {
      const { exportResult, loadResult } = await setup(mockClassificationTask)
      loadResult({
        texts: [
          { id: 'text_1', status: 'completed', label_id: 'pos' },
          { id: 'text_2', status: 'completed', label_id: 'neg' },
        ]
      })
      const data = JSON.parse(exportResult('bob'))
      const valid = validate(data)
      if (!valid) console.error(validate.errors)
      expect(valid).toBe(true)
    })
  })
})
