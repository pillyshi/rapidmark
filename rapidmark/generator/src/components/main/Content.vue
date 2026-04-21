<template>
  <v-row style="height: 100%;" no-gutters>
    <v-col cols="12" style="height: 9%;">
      <ContentHeader />
    </v-col>
    <v-col cols="12" style="height: 1%;"></v-col>
    <v-col cols="12" style="height: 80%;">
      <ContentText />
    </v-col>
    <v-col cols="12" style="height: 1%;"></v-col>
    <v-col cols="12" style="height: 9%;">
      <ContentFooter />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import ContentHeader from './content/ContentHeader.vue'
import ContentText from './content/ContentText.vue'
import ContentFooter from './content/ContentFooter.vue'
</script>

<style scoped>
</style>
