import { computed } from 'vue'
import { useTask } from './useTask'

export interface DerivedLabel {
  id: string
  name: string
  parentId: string | null
  group: string
  short: string
  hue: number
  key: string
}

export interface LabelGroup {
  name: string
  labels: DerivedLabel[]
}

function deriveShort(name: string): string {
  const initials = name
    .split(/[\s_\-/]+/)
    .map((w: string) => w[0]?.toUpperCase() || '')
    .join('')
  return (initials.length >= 2 ? initials : name.slice(0, 4).toUpperCase()).slice(0, 6)
}

function deriveGroup(label: any, allLabels: any[]): string {
  if (label.parentId) {
    const parent = allLabels.find((l: any) => l.id === label.parentId)
    return parent?.name || 'Other'
  }
  return label.group || 'Labels'
}

export const useLabel = () => {
  const { task } = useTask()

  const derivedLabels = computed((): DerivedLabel[] => {
    const raw = task.value?.definition?.labels || []
    // Show root labels (no parentId) as primary labels for annotation
    const roots = raw.filter((l: any) => !l.parentId)
    const total = roots.length

    return roots.map((l: any, i: number) => ({
      id: l.id,
      name: l.name,
      parentId: l.parentId ?? null,
      group: deriveGroup(l, raw),
      short: l.short ?? deriveShort(l.name),
      hue: l.hue ?? Math.round((i / Math.max(total, 1)) * 360),
      key: l.key ?? (i < 9 ? String(i + 1) : ''),
    }))
  })

  const labelGroups = computed((): LabelGroup[] => {
    const map = new Map<string, DerivedLabel[]>()
    for (const l of derivedLabels.value) {
      if (!map.has(l.group)) map.set(l.group, [])
      map.get(l.group)!.push(l)
    }
    return [...map.entries()].map(([name, labels]) => ({ name, labels }))
  })

  const getLabelById = (id: string): DerivedLabel | undefined =>
    derivedLabels.value.find(l => l.id === id)

  // backward compat for components still using rootLabels
  const rootLabels = computed(() => {
    if (!task.value?.definition?.labels) return []
    return task.value.definition.labels.filter((l: any) => !l.parentId)
  })

  const getLabelName = (labelId: string): string => {
    const label = derivedLabels.value.find(l => l.id === labelId)
    return label?.name || labelId
  }

  return { derivedLabels, labelGroups, getLabelById, getLabelName, rootLabels }
}
