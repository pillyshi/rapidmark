<template>
  <v-card style="height: 100%; display: flex; align-items: center;" flat>
    <v-spacer />

    <!-- Navigation Controls -->
    <div class="d-flex align-center gap-2">
      <!-- Previous Button -->
      <v-btn
        variant="outlined"
        size="small"
        :disabled="isFirstText"
        @click="goToPrevious"
      >
        <v-icon size="small" class="mr-1">mdi-chevron-left</v-icon>
        Prev
      </v-btn>

      <!-- Text Index Display -->
      <v-chip size="small" variant="outlined" color="primary">
        {{ currentTextIndex + 1 }} / {{ totalTexts }}
      </v-chip>

      <!-- Status Controls -->
      <v-btn
        :color="currentStatus === 'completed' ? 'success' : 'primary'"
        :variant="currentStatus === 'completed' ? 'flat' : 'outlined'"
        size="small"
        @click="toggleComplete"
      >
        <v-icon size="small" class="mr-1">
          {{ currentStatus === 'completed' ? 'mdi-check-circle' : 'mdi-check' }}
        </v-icon>
        {{ currentStatus === 'completed' ? 'Completed' : 'Done' }}
      </v-btn>

      <v-btn
        :color="currentStatus === 'excluded' ? 'warning' : 'grey'"
        :variant="currentStatus === 'excluded' ? 'flat' : 'outlined'"
        size="small"
        @click="toggleExclude"
      >
        <v-icon size="small" class="mr-1">
          {{ currentStatus === 'excluded' ? 'mdi-cancel' : 'mdi-minus-circle-outline' }}
        </v-icon>
        {{ currentStatus === 'excluded' ? 'Excluded' : 'Exclude' }}
      </v-btn>

      <!-- Next Button -->
      <v-btn
        variant="outlined"
        size="small"
        :disabled="isLastText"
        @click="goToNext"
      >
        Next
        <v-icon size="small" class="ml-1">mdi-chevron-right</v-icon>
      </v-btn>

      <!-- Next Incomplete Button -->
      <v-btn
        variant="text"
        size="small"
        color="primary"
        :disabled="!hasIncomplete"
        @click="goToNextIncomplete"
      >
        <v-icon size="small" class="mr-1">mdi-arrow-right</v-icon>
        Next incomplete
      </v-btn>
    </div>

    <v-spacer />
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTask } from '../../../composables/useTask'
import { useStatus } from '../../../composables/useStatus'

const { task, currentTextIndex } = useTask()
const { statuses, currentStatus, setCurrentStatus } = useStatus()

const totalTexts = computed(() => {
  return task.value?.texts?.length || 0
})

const isFirstText = computed(() => {
  return currentTextIndex.value <= 0
})

const isLastText = computed(() => {
  return currentTextIndex.value >= totalTexts.value - 1
})

const hasIncomplete = computed(() => {
  return statuses.value.some(status => status === 'pending')
})

const goToPrevious = () => {
  if (!isFirstText.value) {
    currentTextIndex.value = currentTextIndex.value - 1
  }
}

const goToNext = () => {
  if (!isLastText.value) {
    currentTextIndex.value = currentTextIndex.value + 1
  }
}

const goToNextIncomplete = () => {
  const currentIndex = currentTextIndex.value

  // Search from current position forward
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

const toggleComplete = () => {
  if (currentStatus.value === 'completed') {
    setCurrentStatus('pending')
  } else {
    setCurrentStatus('completed')
  }
}

const toggleExclude = () => {
  if (currentStatus.value === 'excluded') {
    setCurrentStatus('pending')
  } else {
    setCurrentStatus('excluded')
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>
