import { computed, ref } from 'vue'

declare global {
  const __TASK_CONFIG__: any
  const __RESULT_CONFIG__: any
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

interface Label {
  id: string
  name: string
  parentId: string | null
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
