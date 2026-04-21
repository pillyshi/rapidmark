<template>
  <div>
    <v-card>
      <v-card-title>
        Entities
        <v-spacer />
        <v-chip variant="outlined" size="small">
          {{ currentEntities.length }}
        </v-chip>
      </v-card-title>

      <v-card-text class="entity-list-container">
        <div v-if="currentEntities.length === 0" class="text-center text-grey">
          No entities
        </div>

        <v-list v-else>
          <v-list-item
            v-for="entity in currentEntities"
            :key="entity.id"
            class="entity-item"
          >
            <v-list-item-title>
              <span
                :style="{
                  backgroundColor: getLabelBackgroundColor(entity.labelId, rootLabels),
                  color: 'white',
                  padding: '2px 4px',
                  borderRadius: '3px',
                  fontWeight: 500,
                  display: 'inline'
                }"
              >{{ entity.quote }}</span>
            </v-list-item-title>

            <v-list-item-subtitle>
              {{ getLabelName(entity.labelId) }}
            </v-list-item-subtitle>

            <template #append>
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                @click="removeEntity(entity.id)"
              />
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getLabelBackgroundColor } from '@/utils/labelColors'
import { useEntity } from '../../../composables/useEntity'
import { useLabel } from '@/composables/useLabel'
import { useTask } from '@/composables/useTask'

const { entities, removeEntity } = useEntity()
const { currentText } = useTask()
const { getLabelName, rootLabels } = useLabel()

const currentEntities = computed(() =>
  entities.value.filter(e => e.textId === currentText.value?.id)
)
</script>

<style scoped>
.entity-list-container {
  max-height: 400px;
  overflow-y: auto;
}
</style>
