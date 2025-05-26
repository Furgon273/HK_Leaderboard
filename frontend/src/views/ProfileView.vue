<template>
  <v-container v-if="profile" fluid>
    <v-row >
      <v-col cols="12" sm="6" md="5" lg="4" class="profile-info-col">
        <v-card>
          <v-card-title class="text-center">
            <v-avatar size="120" class="mb-4">
              <v-img :src="profile.avatar || 'https://cdn.vuetifyjs.com/images/john.jpg'" />
            </v-avatar>
            <div>{{ profile.username }}</div>
          </v-card-title>

          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title>Телеграм:</v-list-item-title>
                <v-list-item-subtitle>{{ profile.telegram || 'Не указан' }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title>Discord:</v-list-item-title>
                <v-list-item-subtitle>{{ profile.discord || 'Не указан' }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title>О себе:</v-list-item-title>
                <v-list-item-subtitle>{{ profile.bio || 'Нет информации' }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
          <v-card v-if="isCurrentUserProfile" class="mt-4">
            <v-btn color="primary" block @click="router.push('/profile/edit')">
              Редактировать профиль
            </v-btn>
            <v-btn color="primary" block class="mt-2" @click="router.push('/add-achievement')">
              Добавить достижение
            </v-btn>
          </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="7" lg="8" >
        <!-- Achievements Section -->
        <v-card class="mt-4">
          <v-card-title>Достижения пользователя</v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Сложность</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="achievement in achievements" :key="achievement.id">
                  <td>{{ achievement.title }}</td>
                  <td>{{ achievement.difficulty }}</td>
                  <td>
                    <v-icon v-if="achievement.is_pending" color="orange">mdi-clock-outline</v-icon>
                    <v-icon v-else-if="achievement.is_confirmed" color="success">mdi-check</v-icon>
                    <v-icon v-else-if="achievement.rejected" color="error">mdi-close</v-icon>
                  </td>
                  <td>
                    <v-btn 
                      v-if="isCurrentUserProfile"
                      small
                      @click="router.push(`/edit-achievement/${achievement.id}`)"
                      icon
                    >
                    <v-icon>mdi-pencil</v-icon></v-btn>                  
                  </td>
                </tr>
              </tbody>
            </v-table>
            <p v-if="achievements.length === 0">У пользователя пока нет достижений.</p>
          </v-card-text>
        </v-card>



      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useAuthStore } from '@/store/auth';


const router = useRouter()
 
const route = useRoute()
const { fetchApi } = useApi()

const profile = ref(null)
const achievements = ref([])


const authStore = useAuthStore();
const isCurrentUserProfile = computed(() => {
  return authStore.user?.username === route.params.username;
});

onMounted(async () => {
  const username = route.params.username
  const response = await fetchApi(`/profile/${username}`);
  profile.value = response;
  achievements.value = response.achievements || [];
});
</script>
<style scoped>
.profile-container {
  width: 80%; /* Or a larger percentage */
  margin: 20px auto; /* Centers the block and adds vertical space */
  padding: 20px; /* Keep your existing padding */
}
.v-btn  {
  font-size: 12px;
}
</style>