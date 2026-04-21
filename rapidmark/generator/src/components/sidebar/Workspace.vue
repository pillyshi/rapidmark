<template>
  <div>
    <v-tabs v-model="activeTab">
      <v-tab value="entity">Entity</v-tab>
      <v-tab value="comment">Comment</v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item value="entity">
        <Entity />
      </v-window-item>
      <v-window-item value="comment">
        <Comment />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Entity from './workspace/Entity.vue'
import Comment from './workspace/Comment.vue'

const activeTab = ref('entity')
</script>

<style scoped>
</style>
