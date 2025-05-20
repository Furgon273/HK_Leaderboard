<template>
  <v-container v-if="users.length">
    <v-card>
      <v-card-title>Панель администратора</v-card-title>
        <v-card-title>Список челленджей</v-card-title>
          <v-card-text>
            <v-table v-if="challenges.length">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Название</th>
                  <th>Сложность</th>
                  <th>Лига</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="challenge in challenges" :key="challenge.id">
                  <td>{{ challenge.id }}</td>
                  <td>
                    <router-link :to="{ name: 'ChallengeDetail', params: { id: challenge.id } }">{{ challenge.name }}</router-link>
                  </td>
                  <td>{{ challenge.difficulty }}</td>
                  <td>{{ challenge.league }}</td>
                  <td>
                    <v-btn
                      small
                      color="red"
                      @click="confirmDeletion('challenge', challenge.id, challenge.name)">
                        Удалить
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
            <p v-else>Нет доступных челленджей.</p>
            <v-btn
              color="green"
              @click="$router.push({ name: 'AddChallenge' })"
              style="margin-top: 16px;"
            >
              Добавить челлендж
            </v-btn>

          </v-card-text>

        <v-card style="margin-top: 20px;" color="surface">
          <v-card-title>Список пользователей</v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Имя</th>
                  <th>Роль</th>
                  <th>Действия</th>

                  <th>Удаление</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">

                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.is_super_admin ? 'супер-админ' : user.role }}</td>
                  <!-- Combine action buttons into one cell -->
                  <td>
                    <div style="display: flex; gap: 8px;">
                      <v-btn
                        v-if="!user.is_super_admin && user.role !== 'admin'"
                        @click="makeAdmin(user.id)"
                        color="primary"
                        small
                      >
                        Сделать админом
                      </v-btn>
                      <v-btn
                        v-if="authStore.user?.is_super_admin && user.role === 'admin' && !user.is_super_admin"
                        @click="demoteUser(user.id)"
                        color="orange"
                        small
                      >
                        Разжаловать
                      </v-btn>
                    </div>
                  </td>
                  <td>
                    <v-btn
                      v-if="authStore.user?.is_super_admin && !user.is_super_admin"
                      @click="confirmDeletion('user', user.id, user.username)"
                      color="red darken-1"
                      small
                    >
                      Удалить
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>

        <v-dialog v-model="showModal" max-width="500px">
          <v-card color="surface">
            <v-card-title class="headline">Подтверждение удаления</v-card-title>
            <v-card-text>
              Вы уверены, что хотите удалить {{ itemType === 'challenge' ? 'челлендж' : 'пользователя' }}: {{ itemName }}?
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="showModal = false">Отмена</v-btn>
              <v-btn color="red darken-1" text @click="performDeletion()">Удалить</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
    </v-card>
  </v-container>
  <v-container v-else>
    <v-card>
      <v-card-title>Загрузка данных...</v-card-title>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/store/auth';
const authStore = useAuthStore();

const { fetchApi } = useApi()
const users = ref([])

const showModal = ref(false);
const itemToDeleteId = ref(null);
const itemType = ref(null); // 'challenge' or 'user'
const itemName = ref(''); // To display the name of the item in the modal
const challenges = ref([]);

onMounted(async () => {
  try {
    users.value = await fetchApi('/users')
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
    // Добавьте уведомление для пользователя
  }

  try {
    challenges.value = await fetchApi('/challenges');
  } catch (error) {
    console.error('Ошибка загрузки челленджей:', error);
  }

  console.log('Auth Store User:', authStore.user);
  console.log('Users List:', users.value);
})
const router = useRouter(); // Get router instance

const makeAdmin = async (userId) => {
  try {
    await fetchApi(`/users/${userId}/make_admin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    users.value = await fetchApi('/users')
  } catch (error) {
    console.error('Ошибка назначения админа:', error)
  }
}

const confirmDeletion = (type, id, name) => {
  itemType.value = type;
  itemToDeleteId.value = id;
  itemName.value = name;
  showModal.value = true;
};

const performDeletion = async () => {
  if (itemType.value === 'challenge') {
    await deleteChallenge(itemToDeleteId.value);
  } else if (itemType.value === 'user') {
    await deleteUser(itemToDeleteId.value);
  }
  showModal.value = false;
};

const cancelDeletion = () => { showModal.value = false; };

const deleteChallenge = async (challengeId) => {
  try {
 await fetchApi(`/challenges/${challengeId}`, {
      method: 'DELETE',
    });
 challenges.value = await fetchApi('/challenges'); // Refresh the list
  } catch (error) {
 console.error('Ошибка удаления челленджа:', error);
  }
};

const deleteUser = async (userId) => {
  try {
    await fetchApi(`/users/${userId}`, {
      method: 'DELETE',
    });
    users.value = await fetchApi('/users'); // Refresh the list
  } catch (error) {
    console.error('Ошибка удаления пользователя:', error);
  }
};

const demoteUser = async (userId) => {
  try {
    await fetchApi(`/users/${userId}/demote`, {
      method: 'POST',
    });
    users.value = await fetchApi('/users'); // Refresh the list
  } catch (error) {
    console.error('Ошибка разжалования пользователя:', error);
  }
};

</script>