<template>
  <v-card style="height: 100%;">
    <v-card-title>
      {{ currentTextId || 'Loading...' }}
    </v-card-title>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useTask } from '../../../composables/useTask'

const { task, currentText, loadTask } = useTask()

const currentTextId = computed(() => {
  return currentText.value?.id
})

onMounted(() => {
  loadTask()
})
</script>

<style scoped>
</style>
