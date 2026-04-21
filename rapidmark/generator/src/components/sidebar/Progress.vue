<template>
  <v-card class="mb-4">
    <v-card-text>
      <!-- Overall Progress Bar -->
      <div class="mb-4">
        <div class="d-flex justify-space-between mb-2">
          <span class="text-body-2">Overall progress</span>
          <span class="text-body-2">{{ completedCount }}/{{ totalCount }}</span>
        </div>
        <v-progress-linear
          :model-value="overallProgress"
          :color="progressColor"
          height="8"
          rounded
        />
        <div class="text-center text-caption mt-1">
          {{ Math.round(overallProgress) }}%
        </div>
      </div>

    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useStatus } from '../../composables/useStatus'
import { useTask } from '../../composables/useTask'

const { statuses } = useStatus()
const { task, currentTextIndex } = useTask()

const totalCount = computed(() => {
  return task.value?.texts?.length || 0
})

const completedCount = computed(() => {
  return statuses.value.filter(status => status === 'completed').length
})

const pendingCount = computed(() => {
  return statuses.value.filter(status => status === 'pending').length
})

const excludedCount = computed(() => {
  return statuses.value.filter(status => status === 'excluded').length
})

const overallProgress = computed(() => {
  if (totalCount.value === 0) return 0
  return (completedCount.value / totalCount.value) * 100
})

const progressColor = computed(() => {
  const progress = overallProgress.value
  if (progress === 100) return 'success'
  if (progress >= 75) return 'info'
  if (progress >= 50) return 'warning'
  return 'primary'
})

const hasIncomplete = computed(() => {
  return pendingCount.value > 0
})

const goToNextIncomplete = () => {
  const currentIndex = currentTextIndex.value
  for (let i = currentIndex + 1; i < statuses.value.length; i++) {
    if (statuses.value[i] === 'pending') {
      currentTextIndex.value = i
      return
    }
  }
  // If not found after current, search from beginning
  for (let i = 0; i < currentIndex; i++) {
    if (statuses.value[i] === 'pending') {
      currentTextIndex.value = i
      return
    }
  }
}

const goToFirstText = () => {
  currentTextIndex.value = 0
}
</script>

<style scoped>
</style>
