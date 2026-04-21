<template>
  <v-main style="height: 92%;">
    <v-container fluid style="height: 100%;">
      <v-row style="height: 100%;">
        <v-col cols="8" style="height: 100%;">
          <Content />
        </v-col>
        <v-col cols="4" style="height: 100%;">
          <Sidebar />
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup lang="ts">
import Content from './main/Content.vue'
import Sidebar from './main/Sidebar.vue'
</script>

<style scoped>
</style>
