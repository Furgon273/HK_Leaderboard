<template>
  <v-container>
    <v-card v-if="achievement">
      <v-card-title>{{ achievement.title }}</v-card-title>
      <!-- Assuming the backend returns 'title' not 'name' -->
      <!-- <v-card-title>{{ achievement.title }}</v-card-title> -->
      <v-card-text>
        <p><strong>Difficulty:</strong> {{ achievement.difficulty }}</p>
        <p><strong>Description:</strong> {{ achievement.description }}</p>
        <p v-if="achievement.link">
          <strong>Link: </strong><router-link :to="{ path: '/confirm-link', query: { url: achievement.link } }">{{ achievement.link }}</router-link>
        </p>
        <!-- Display other achievement details as needed -->
      </v-card-text>
    </v-card>
    <v-alert v-else-if="error" type="error">{{ error }}</v-alert>
    <v-progress-circular v-else indeterminate color="primary"></v-progress-circular>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useApi } from '@/composables/useApi';

const route = useRoute();
const achievement = ref(null);
const error = ref(null);
const { fetchApi } = useApi();

onMounted(async () => {
  const achievementId = route.params.id;
  if (!achievementId) {
    error.value = 'Achievement ID is missing.';
    return;
  }

  try {
    const response = await fetchApi(`/achievements/${achievementId}`);
    achievement.value = response;
  } catch (err) {
    error.value = 'Failed to fetch achievement details.';
    console.error('Error fetching achievement details:', err);
  }
});
</script>

<style scoped>
/* Add any specific styles for this component here */
</style>