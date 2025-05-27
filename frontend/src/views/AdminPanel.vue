<template>
  <!-- Test comment -->
    <div class="admin-panel-container">
      <v-card>
        <v-card-title class="admin-panel-title">
          <span style="width: 100%; text-align: center;">Панель администратора</span>
        </v-card-title>

        <v-divider></v-divider>

        <div class="tables-container">
          <!-- Достижения -->
          <v-card class="table-card">
            <v-card-title>Достижения</v-card-title>
            <v-card-text>
              <v-table dense fixed-header :height="tableHeight">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Сложность</th>
                    <th>Пользователь</th>
                    <th>Статус</th>
                    <th class="action-buttons-cell">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="achievement in achievements" :key="achievement.id">
                    <td>{{ achievement.id }}</td>
                    <td>
                      <router-link :to="{ name: 'AchievementDetails', params: { id: achievement.id } }">{{ truncateTitle(achievement.title) }}</router-link>
                    </td>
                    <td>{{ achievement.difficulty }}</td>
                    <td>{{ achievement.username }}</td>
                    <!-- <td>{{ achievement.is_pending ? 'В ожидании' : (achievement.is_confirmed ? 'Подтверждено' : 'Отклонено') }}</td> -->
                    <td>
                      <v-icon v-if="achievement.is_pending" color="orange">mdi-clock-outline</v-icon>
                      <v-icon v-if="achievement.is_confirmed" color="success">mdi-check</v-icon>
                      <v-icon v-if="!achievement.is_pending && !achievement.is_confirmed" color="red">mdi-close</v-icon>
                    </td>                    
                    <td class="action-buttons-cell">
                      <div class="action-buttons">
                        <v-btn
                          :size="buttonSize"
                          color="secondary"
                          @click="editAchievement(achievement.id)"
                          icon
                        >
                          <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn
                          v-if="!achievement.is_confirmed && !achievement.rejected"
                          :size="buttonSize"
                          color="success"
                          @click="confirmAchievement(achievement.id)"
                          icon
                        >
                          <v-icon>mdi-check</v-icon>
                        </v-btn>
                        <v-btn
                          v-if="achievement.is_pending || achievement.is_confirmed"
                          :size="buttonSize"
                          color="error"
                          @click="rejectAchievement(achievement.id)"
                          icon
                        >
                          <v-icon>mdi-close</v-icon>
                        </v-btn>
                        <v-btn
                          :size="buttonSize"
                          color="red"
                          @click="confirmDeletion('achievement', achievement.id, achievement.title)"
                          icon
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>

          <!-- Пользователи -->
          <v-card class="table-card">
            <v-card-title>Список пользователей</v-card-title>
            <v-card-text>
              <v-table dense fixed-header :height="tableHeight">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Имя</th>
                    <th>Роль</th>
                    <th v-if="authStore.user?.is_super_admin">Действия</th>
                    <th>Удаление</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td>{{ truncateTitle(user.username) }}</td>
                    <td>{{ user.is_super_admin ? 'супер-админ' : (user.role === 'admin' ? 'админ' : 'пользователь') }}</td>
                    <td v-if="authStore.user?.is_super_admin" class="action-buttons-cell">
                      <div class="action-buttons">
                        <v-btn
                          v-if="!user.is_admin && !user.is_super_admin"
                          @click="toggleAdmin(user)"
                          :size="buttonSize"
                        >
                          {{ user.role === 'admin' ? 'Разжаловать' : 'Сделать админом' }}
                        </v-btn>
                        <!-- Removed the second button and combined the logic into one -->
                        <!-- <v-btn
                          v-if="user.role === 'admin' && !user.is_super_admin"
                          @click="toggleAdmin(user)"
                          :size="buttonSize"
                        > -->
                      </div>
                    </td>
                    <td class="action-buttons-cell">
                      <v-btn
                        v-if="authStore.user?.is_super_admin && !user.is_super_admin"
                        @click="confirmDeletion('user', user.id, user.username)"
                        color="red darken-1"
                        size="buttonSize"
                        icon
                      >
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </div>
      </v-card>
    </div>

    <!-- Диалог подтверждения удаления -->
    <v-dialog v-model="showModal" max-width="500px">
      <v-card color="surface">
        <v-card-title class="headline">Подтверждение удаления</v-card-title>
        <v-card-text v-if="itemType && itemName">
          Вы уверены, что хотите удалить {{ itemType === 'challenge' ? 'челлендж' : 'пользователя' }}: {{ itemName }}?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="showModal = false">Отмена</v-btn>
          <v-btn color="red darken-1" text @click="performDeletion()">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter} from 'vue-router';
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();
const { fetchApi } = useApi();
const users = ref([]);
const achievements = ref([]);
const showModal = ref(false);
const itemToDeleteId = ref(null);
const itemType = ref(null);
const itemName = ref('');

// Адаптивные размеры
const buttonSize = computed(() => {
  return window.innerWidth < 768 ? 'x-small' : 'small';
});

const tableHeight = computed(() => {
  return window.innerHeight < 800 ? '400px' : '500px';
});

watch(() => authStore.user, (newUser) => {
  if (newUser && newUser.is_admin) {
    fetchUsers();
    fetchAchievements();
  }
});

const fetchUsers = async () => {
  const fetchedUsers = await fetchApi('/users', { method: 'GET' });
  users.value = fetchedUsers;
};


const fetchAchievements = async () => {
  // const achievements = (await get('/achievements')).data;
  // console.log("Fetched achievements:", achievements);
  const fetchedAchievements = await fetchApi('/achievements');
  console.log(fetchedAchievements);

  // Sort the achievements: pending, then rejected, then confirmed
  fetchedAchievements.sort((a, b) => {
    if (a.is_pending && !b.is_pending) return -1; // a is pending, b is not -> a comes first
    if (!a.is_pending && b.is_pending) return 1; // b is pending, a is not -> b comes first
    if (a.rejected && !b.rejected) return -1; // a is rejected, b is not -> a comes first
    if (!a.rejected && b.rejected) return 1; // b is rejected, a is not -> b comes first
    if (a.is_confirmed && !b.is_confirmed) return 1; // a is confirmed, b is not -> a comes first
    if (!a.is_confirmed && b.is_confirmed) return -1; // b is confirmed, a is not -> b comes first
    return 0; // same status, maintain original order
  });

  // Assign the sorted data to the achievements ref
  achievements.value = fetchedAchievements;
};

const router = useRouter(); // Get router instance

onMounted(async () => {
  await fetchUsers();
  await fetchAchievements();
});

const confirmDeletion = (type, id, name) => {
  itemType.value = type;
  itemToDeleteId.value = id;
  itemName.value = name;
  showModal.value = true;
};

const performDeletion = async () => {
  if (itemType.value === 'achievement') {
    await deleteAchievement(itemToDeleteId.value);
  } else if (itemType.value === 'user') {
    await deleteUser(itemToDeleteId.value);
  }
  showModal.value = false;
};

const deleteUser = async (userId) => {
  try {
    await fetchApi(`/users/${userId}`, { method: 'DELETE' });
    await fetchUsers(); // Refresh the user list
  } catch (error) {
    console.error('Error deleting user:', error);
  }
};

const confirmAchievement = async (achievementId) => {
  try {
    await fetchApi(`/achievements/${achievementId}/confirm`, { method: 'POST' });
    fetchAchievements();
  } catch (error) {
    console.error('Error confirming achievement:', error);
  }
};

const rejectAchievement = async (achievementId) => {
  try {
    await fetchApi(`/achievements/${achievementId}/reject`, { method: 'POST' });
    fetchAchievements();
  } catch (error) {
    console.error('Error rejecting achievement:', error);
  }
};

const deleteAchievement = async (achievementId) => {
  try {
    await fetchApi(`/achievements/${achievementId}`, { method: 'DELETE' });
    fetchAchievements();
  } catch (error) {
    console.error('Error deleting achievement:', error);
  }
};

const toggleAdmin = async (user) => {
  console.log('toggleAdmin called with user:', user);
  if (!user) { console.error('User object is undefined in toggleAdmin'); return; }
  try {
    const endpoint = user.role === 'admin' ? `/users/${user.id}/demote` : `/users/${user.id}/make_admin`;
    await fetchApi(endpoint, { method: 'POST' });
    await fetchUsers(); // Refresh the list
  } catch (error) {
    console.error(`Error toggling admin status for user ${user.id}:`, error);
  }
};

const editAchievement = async (achievementId) => {
 router.push({ name: 'EditAchievement', params: { id: achievementId } });
};

const truncateTitle = (title) => {
  return title.length > 17 ? title.substring(0, 17) + '...' : title;
};

</script>

<style scoped>
/* Основные стили */
.admin-panel-container {
  width: 100%;
  max-width: 1800px;
  margin: 0 auto;
  padding: 20px;
}

/* Карточка-обертка */
.v-card {
  width: 100%;
  margin: 0 auto;
  background-color: #2d2d2d;
  border-radius: 8px;
  overflow: hidden;
}

/* Заголовок */
.admin-panel-title {
  padding: 16px;
  text-align: center;
  background-color: #252525;
  color: white;
}

/* Контейнер таблиц */
.tables-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  padding: 20px;
  width: 100%;
}

/* Карточки таблиц */
.table-card {
  background-color: #333;
  border-radius: 6px;
  overflow-x: auto;
}

/* Таблицы */
.v-table {
  width: 100%;
  min-width: 100%;
}

/* Адаптация */
@media (min-width: 1500px) {
  .tables-container {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .admin-panel-container {
    padding: 10px;
  }
}
</style>