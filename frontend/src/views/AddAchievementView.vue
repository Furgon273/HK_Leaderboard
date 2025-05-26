<template>
  <div class="add-achievement">
    <h1>Add New Achievement</h1>
    <form @submit.prevent="submitAchievement">
      <div>
        <label for="title">Title:</label>
        <input type="text" id="title" v-model="achievement.title" required>
      </div>
      <div>
        <label for="description">Description:</label>
        <textarea id="description" v-model="achievement.description"></textarea>
      </div>
      <div>
        <label for="difficulty">Difficulty (1-100):</label>
        <input type="number" id="difficulty" v-model="achievement.difficulty" min="1" max="100" required>
      </div>
      <div>
        <label for="link">Link (Optional):</label>
        <input type="text" id="link" v-model="achievement.link">
      </div>
      <button type="submit">Add Achievement</button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/store/auth';

export default {
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const { fetchApi } = useApi();

    const achievement = ref({
      title: '',
      description: '',
      difficulty: 1,
      link: '',
    });

    const submitAchievement = async () => {
      try {
        const response = await fetchApi('/achievements', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(achievement.value),
        });
        console.log('Achievement added:', response); // Adjusted log based on fetchApi return
        // Redirect to user profile after successful submission
        // Assuming user ID can be retrieved or is available
        // For now, redirecting to a placeholder. You might need to adjust this
        // based on how you get the current user's ID in your frontend.
        const currentUserId = localStorage.getItem('user_id'); // Example: Get user ID from localStorage
        router.push({ name: 'profile', params: { username: authStore.user?.username } });
      } catch (error) {
        console.error('Error adding achievement:', error);
        // Handle error (e.g., show error message to user)
      }
    };

    return {
      achievement,
      submitAchievement,
    };
  },
};
</script>

<style scoped>
.add-achievement {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.add-achievement div {
  margin-bottom: 15px;
}

.add-achievement label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.add-achievement input[type="text"],
.add-achievement input[type="number"],
.add-achievement textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.add-achievement button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.add-achievement button:hover {
  background-color: #45a049;
}
</style>