<template>
  <v-app-bar style="height: 8%;">
    <v-app-bar-title>
      {{ taskName || 'Loading task...' }}
    </v-app-bar-title>

    <v-spacer />

    <v-btn
      icon="mdi-upload"
      variant="text"
      @click="handleUpload"
      :disabled="uploading"
    >
      <v-icon>mdi-upload</v-icon>
      <v-tooltip activator="parent" location="bottom">
        Upload
      </v-tooltip>
    </v-btn>

    <v-btn
      icon="mdi-download"
      variant="text"
      @click="handleDownload"
      :disabled="downloading"
    >
      <v-icon>mdi-download</v-icon>
      <v-tooltip activator="parent" location="bottom">
        Download
      </v-tooltip>
    </v-btn>

    <input
      ref="fileInput"
      type="file"
      style="display: none"
      accept=".json"
      @change="onFileSelected"
    />
  </v-app-bar>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTask } from '../composables/useTask'
import { useEntity } from '../composables/useEntity'
import { useStatus } from '../composables/useStatus'
import { useResult } from '../composables/useResult'

const { task } = useTask()
const { entities } = useEntity()
const { statuses } = useStatus()
const { loadResult } = useResult()

const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const downloading = ref(false)

const taskName = computed(() => task.value?.definition?.name)

const buildExportData = () => {
  const taskInfo = {
    taskType: task.value?.definition?.type || 'ner',
    taskTitle: task.value?.definition?.name || '',
    taskDescription: task.value?.definition?.description || '',
    taskId: task.value?.definition?.id || '',
    exportedAt: new Date().toISOString(),
    exportFormat: 'unified_v1'
  }

  const results: Record<string, any> = {}
  task.value?.texts?.forEach((text, index) => {
    results[text.id] = {
      status: statuses.value[index] || 'pending',
      attributes: text.attributes || {},
      entities: []
    }
  })

  entities.value.forEach((entity: any) => {
    const textId = entity.textId
    if (textId && results[textId]) {
      results[textId].entities.push({
        id: entity.id,
        start: entity.start,
        end: entity.end,
        text: entity.quote,
        label: entity.labelId
      })
    }
  })

  return { taskInfo, results }
}

const handleDownload = () => {
  downloading.value = true
  try {
    const data = buildExportData()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const taskId = task.value?.definition?.id || 'unknown'
    const workerName = import.meta.env.RAPIDMARK_WORKER_NAME
    link.download = workerName
      ? `${taskId}.${workerName}.result.rapidmark.json`
      : `${taskId}.result.rapidmark.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
  } finally {
    downloading.value = false
  }
}

const handleUpload = () => {
  fileInput.value?.click()
}

const onFileSelected = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  uploading.value = true
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target?.result as string)
      loadResult(data)
      if (fileInput.value) fileInput.value.value = ''
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed. Please check the file format.')
    } finally {
      uploading.value = false
    }
  }
  reader.readAsText(file)
}
</script>

<style scoped>
</style>
