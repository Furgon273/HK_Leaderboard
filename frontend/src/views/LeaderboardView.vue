<template>
  <v-container fluid class="pa-2 pa-sm-4">
    <v-row justify="center">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex flex-column flex-sm-row justify-space-between align-center">
            <span class="text-h5 mb-2 mb-sm-0">Топ игроков</span>
            <v-chip v-if="lastUpdated" color="info" small>
              Обновлено: {{ lastUpdated.toLocaleTimeString() }}
            </v-chip>
          </v-card-title>

          <v-card-text class="pa-0">
            <v-data-table
              :headers="headers"
              :items="leaderboard"
              :items-per-page="-1"
              hide-default-footer            
              class="elevation-1"
              dense
            >
              <template v-slot:item.username="{ item }">
                <router-link :to="`/profile/${item.username}`">
                  {{ item.username }}
                </router-link>
              </template>
              <template v-slot:item.achievements="{ item }">
                <router-link v-for="(ach, achIndex) in item.achievements" :key="ach.id" :to="`/achievements/${ach.id}`">
                  {{ truncateTitle(ach.title) }}{{ achIndex < item.achievements.length - 1 ? ', ' : '' }}
                </router-link>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const { fetchApi } = useApi()
const leaderboard = ref([])
const lastUpdated = ref(null)

const headers = ref([
  { title: '№', key: 'index', sortable: false },
  { title: 'Игрок', key: 'username' },
  { title: 'Лига', key: 'league' },
  { title: 'Достижения', key: 'achievements', sortable: false },
])

onMounted(async () => {
  try {
    const data = await fetchApi('/leaderboard')
    // Add index to each item for the numbered column
    leaderboard.value = data.map((item, index) => ({ ...item, index: index + 1 }));
    lastUpdated.value = new Date()
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    // Handle error, e.g., show an error message to the user
  }
})

const truncateTitle = (title) => {
  if (title.length > 17) {
    return title.substring(0, 17) + '...'
  }
  return title
}
</script>

<style scoped>
/* You can add specific styles here if needed for further customization */
/* For example, adjusting column widths for specific breakpoints */
</style>