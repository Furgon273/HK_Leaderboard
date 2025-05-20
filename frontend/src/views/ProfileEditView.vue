<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Редактирование профиля</v-card-title>
          <v-card-text>
            <v-form>
              <v-text-field
                label="Телеграм"
                v-model="telegram"
              ></v-text-field>
              
              <v-text-field
                label="Discord"
                v-model="discord"
              ></v-text-field>
              
              <v-textarea
                label="О себе"
                v-model="bio"
              ></v-textarea>
              
              <v-btn 
                color="primary" 
                @click="saveProfile"
                v-bind:loading="loading">Сохранить</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router'; // Import useRouter
  import { useApi } from '@/composables/useApi';
  import { useAuthStore } from '@/store/auth';

  const route = useRoute();
  const { fetchApi } = useApi();
  const authStore = useAuthStore();

  const router = useRouter(); // Get router instance
  const telegram = ref(null);
  const discord = ref(null);
  const bio = ref(null);

  const loading = ref(false);
  const errorMessage = ref(null);

  onMounted(async () => {
    if (authStore.user && authStore.user.username) {
      loading.value = true;
      errorMessage.value = null;
      try {
        const profileData = await fetchApi(`/profile/${authStore.user.username}`);
        telegram.value = profileData.telegram;
        discord.value = profileData.discord;
        bio.value = profileData.bio;
        console.log("Profile data loaded:", { telegram: telegram.value, discord: discord.value, bio: bio.value });
      } catch (error) {
        console.error("Error fetching profile data:", error);
        errorMessage.value = "Не удалось загрузить данные профиля.";
      } finally {
        loading.value = false;
      }
    } else {
      // console.warn("User not authorized or username not available in auth store.");
    }
  });

  // Функция для сохранения профиля
  const saveProfile = async () => {
    // Проверяем, что пользователь авторизован
    if (!authStore.user || !authStore.user.username) {
      // Можно добавить логику перенаправления или сообщения об ошибке
      return;
    }

    loading.value = true; // Начинаем сохранение
    errorMessage.value = null; // Сбрасываем предыдущие ошибки

    const data = {
      telegram: telegram.value,
      discord: discord.value,
      bio: bio.value,
    };

    try {
      await fetchApi(`/profile/me`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      console.log("Profile updated successfully!");
      router.push(`/profile/${authStore.user.username}`); // Navigate to profile page
      // Можно добавить сообщение об успешном сохранении для пользователя
    } catch (error) {
      console.error("Error saving profile:", error);
      errorMessage.value = "Не удалось сохранить профиль.";
    } finally {
      loading.value = false; // Заканчиваем сохранение
    }
  };
</script>

<style scoped lang="css">
/* General container and card styling */
.v-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
  /* Inherits background from main.css */
  color: var(--text-color); /* Use the text color from example */
}

.v-card {
  background-color: var(--card-bg); /* Dark card background */
  border-radius: 8px;
  border: 1px solid #333; /* Subtle border */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5); /* Darker shadow */
  color: var(--text-color); /* Ensure text inside card is readable */
}

.v-card-title {
  color: var(--accent-color); /* White title */
  font-size: 24px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #333;
}

/* Form element styling */
.v-form {
  padding-top: 10px;
}

.v-text-field,
.v-textarea {
  background-color: #3a3a3a; /* Darker input background */
  color: #ffffff; /* White text in inputs */
  border: 1px solid #555; /* Lighter border */
  border-radius: 4px;
}
</style>