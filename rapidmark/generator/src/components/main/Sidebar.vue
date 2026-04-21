<template>
  <div>
    <Progress />
    <Workspace />
  </div>
</template>

<script lang="ts">
import Progress from '../sidebar/Progress.vue'
import Workspace from '../sidebar/Workspace.vue'

export default {
  name: 'Sidebar',
  components: {
    Progress,
    Workspace
  }
}
</script>

<style scoped>
</style>