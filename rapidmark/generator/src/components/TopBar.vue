<template>
  <header class="topbar">
    <div class="topbar-left">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">◤</span>
        <span class="brand-name">RapidMark</span>
      </div>
      <div class="sep" />
      <div class="task-name">
        <span v-if="loading" class="shimmer" style="width: 280px">&nbsp;</span>
        <template v-else>
          <span class="task-kicker">TASK</span>
          <span class="task-title" :title="taskName">{{ taskName }}</span>
        </template>
      </div>
    </div>

    <div class="topbar-right">
      <div class="local-badge" title="This page makes no server requests">
        <span class="dot" />
        <span class="local-text">
          <b>LOCAL-ONLY</b>
          <em>No external requests</em>
        </span>
      </div>

      <div class="worker">
        <label for="worker-input">WORKER</label>
        <input
          id="worker-input"
          :value="worker"
          @input="$emit('update:worker', ($event.target as HTMLInputElement).value)"
          placeholder="(not set)"
          spellcheck="false"
          autocomplete="off"
        />
      </div>

      <button class="btn ghost" @click="$emit('import')">
        <span aria-hidden="true">↥</span>&nbsp;Import result
      </button>
      <button class="btn primary" @click="$emit('export')">
        <span aria-hidden="true">↧</span>&nbsp;Export JSON
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  taskName: string
  loading: boolean
  worker: string
}>()

defineEmits<{
  'update:worker': [value: string]
  import: []
  export: []
}>()
</script>
