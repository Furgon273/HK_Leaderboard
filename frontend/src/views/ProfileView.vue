<template>
  <v-container v-if="profile" fluid>
    <v-row >
      <v-col cols="12" sm="6" md="5" lg="4">
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
          </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="7" lg="8">
        <v-card>
          <v-card-title>Забеги пользователя</v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>Челлендж</th>
                  <th>Статус</th>
                  <th>Дата</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="run in runs" :key="run.id">
                  <td>{{ run.challenge.name }}</td>
                  <td>
                    <v-chip :color="run.status === 'approved' ? 'success' : 'warning'">
                      {{ run.status === 'approved' ? 'Подтвержден' : 'На модерации' }}
                    </v-chip>
                  </td>
                  <td>{{ new Date(run.submitted_at).toLocaleString() }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter} from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useAuthStore } from '@/store/auth';


const router = useRouter();

const route = useRoute()
const { fetchApi } = useApi()

const profile = ref(null)
const runs = ref([])

const authStore = useAuthStore();
const isCurrentUserProfile = computed(() => {
  return authStore.user?.username === route.params.username;
});

onMounted(async () => {
  const username = route.params.username
  profile.value = await fetchApi(`/profile/${username}`)
  runs.value = profile.value.runs
})
</script>
