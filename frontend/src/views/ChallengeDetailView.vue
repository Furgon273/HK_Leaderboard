<template>
  <div class="container">
    <div v-if="challenge">
      <h1>{{ challenge.name }}</h1>
      <p><strong>Description:</strong> {{ challenge.description }}</p>
      <p><strong>Difficulty:</strong> {{ challenge.difficulty }}</p>
      <p><strong>League:</strong> {{ challenge.league }}</p>

      <!-- <v-btn
      v-if="isAdmin"
              color="red"
      @click="deleteChallenge" style="margin-top: 20px;">Удалить челлендж</v-btn>
      -->
    </div>
    <div v-else>
      <p v-if="!challenge">Loading challenge...</p>
      <p v-else>Challenge not found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router'; // Import useRouter
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/store/auth'; // Import useAuthStore
import { computed } from 'vue'; // Import computed if needed, though simple check is enough

const route = useRoute();
const router = useRouter(); // Get router instance
const { fetchApi } = useApi();
const challenge = ref(null);
const authStore = useAuthStore(); // Get auth store instance

// Check if the user is an administrator
const isAdmin = computed(() => {
  return authStore.user && authStore.user.role === 'admin';
});

const deleteChallenge = async () => {
  const challengeId = route.params.id;
};

onMounted(async () => {
  const challengeId = route.params.id;
  if (!challengeId) {
    console.error("Challenge ID is missing from route params.");
    // Optionally redirect or show an error message to the user
    return;
  }

  try {
    const response = await fetchApi(`/challenges/${challengeId}`);
    if (response) {
      challenge.value = response;
    } else {
      console.error("Challenge not found:", challengeId);
      // Update challenge to indicate not found, e.g., challenge.value = {}; or set an error state
      challenge.value = undefined; // Set to undefined to indicate not found vs null (loading)
    }
  } catch (error) {
    console.error('Error fetching challenge:', error);
    // Optionally set an error state or show an error message
    challenge.value = undefined; // Indicate error or not found
  }
});
</script>

<style scoped>
.container {
  max-width: 960px;
  margin: 40px auto;
  padding: 30px;
  background-color: var(--card-bg); /* Dark background */
  border-radius: 8px;
  border: 1px solid #333;
  color: var(--text-color); /* Light text */
}

h1 {
  font-size: 28px;
  color: var(--accent-color); /* Lighter heading color */
  margin-bottom: 20px;
  border-bottom: 1px solid #555; /* Separator line */
  padding-bottom: 10px;
}

p {
  margin-bottom: 15px;
  line-height: 1.8;
}
</style>