import { describe, expect, it, vi, beforeEach } from 'vitest'
import { useTask } from '../useTask'
import mockTask from "../../__mocks__/task";


describe('useTaskConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('__TASK_CONFIG__', undefined)
    window.__TASK_CONFIG__ = undefined
  })

  describe('Configuration Loading', () => {
    it('loads configuration from __TASK_CONFIG__', async () => {
      vi.stubGlobal('__TASK_CONFIG__', mockTask)
      const { loadTask, task } = useTask()
      await loadTask()
      expect(task.value).toEqual(mockTask)
    })
  })
})
