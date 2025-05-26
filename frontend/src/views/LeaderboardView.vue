<template>
  <v-container>
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Топ игроков</span>
        <v-chip v-if="lastUpdated" color="info">
          Обновлено: {{ lastUpdated.toLocaleTimeString() }}
        </v-chip>
      </v-card-title>
      
      <v-card-text>
        <v-table>
          <thead>
            <tr>
              <th>№</th>
              <th>Игрок</th>
              <th>Достижения</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(player, index) in leaderboard" :key="player.username">
              <td>{{ index + 1 }}</td>
              <td>
                <router-link :to="`/profile/${player.username}`">
                  {{ player.username }}
                </router-link>
              </td>
              <td>
                <router-link v-for="(ach, achIndex) in player.achievements" :key="ach.id" :to="`/achievements/${ach.id}`">
                  {{ ach.title }}{{ achIndex < player.achievements.length - 1 ? ', ' : '' }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </v-table>      </v-card-text>    </v-card>  </v-container></template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const { fetchApi } = useApi()
const leaderboard = ref([])
const lastUpdated = ref(null)

onMounted(async () => {
  leaderboard.value = await fetchApi('/leaderboard')
  lastUpdated.value = new Date()
})
</script>