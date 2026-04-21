<template>
  <v-app class="h-screen overflow-hidden">
    <Header />
    <Main />
  </v-app>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import Header from './components/Header.vue'
import Main from './components/Main.vue'
import { useTask } from './composables/useTask'
import { useStatus } from './composables/useStatus'
import { useResult } from './composables/useResult'

const { loadTask } = useTask()
const { initializeStatuses } = useStatus()
const { loadResult } = useResult()

onMounted(async () => {
  await loadTask()
  initializeStatuses()
  if (__RESULT_CONFIG__ !== null) {
    loadResult(__RESULT_CONFIG__)
  }
})
</script>

<style scoped>
</style>
