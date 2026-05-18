import { computed, ref } from 'vue'

declare global {
  const __TASK_CONFIG__: any
  const __RESULT_CONFIG__: any
}

export interface Field {
  kind: 'full' | 'withoutLabelIds' | 'withoutStructureIds' | 'groupOnly'
  labelIds: string[]
}

interface TaskText {
  id: string
  content: string
  attributes: Record<string, any>
}

export interface Task {
  definition: TaskDefinition
  texts: TaskText[]
}

interface TaskDefinition {
  id: string
  name: string
  type: "ner"
  description: string | null
  labels?: Label[]
}

export interface Label {
  id: string
  name: string
  parentId: string | null
  // Optional design-system fields (may be present in extended task format)
  group?: string
  short?: string
  hue?: number
  key?: string
}

const task = ref<Task | null>(null)
const currentTextIndex = ref<number>(0)
const currentText = computed(() => {
  if (task.value == null) return null
  return task.value.texts[currentTextIndex.value]
})

export function useTask() {
  const loadTask = async (): Promise<void> => {
    task.value = __TASK_CONFIG__
  }

  return {
    task,
    currentTextIndex,
    currentText,
    loadTask,
  }
}
