<template>
  <div class="edit-achievement-view">
    <h1>Edit Achievement</h1>
    <p>Editing achievement with ID: {{ achievementId }}</p>

    <form @submit.prevent="saveAchievement">
      <div class="form-group">
        <label for="achievementName">Achievement Name:</label>
        <input type="text" id="achievementName" v-model="achievement.title" required>
      </div>

      <div class="form-group">
        <label for="achievementDescription">Description:</label>
        <textarea id="achievementDescription" v-model="achievement.description" required></textarea>
      </div>

      <div class="form-group">
        <label for="achievementDifficulty">Difficulty:</label>
        <input type="number" id="achievementDifficulty" v-model="achievement.difficulty" required>
      </div>

      <div class="form-group">
        <label for="achievementLink">Link:</label>
        <input type="text" id="achievementLink" v-model="achievement.link">
      </div>
      <button type="submit">Save Changes</button>
    </form>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useApi } from '@/composables/useApi';

export default {
  name: 'EditAchievementView',
  setup() {
    const route = useRoute();
    const achievementId = ref(null);
    const achievement = ref({
      name: '',
      description: '',
 difficulty: 0,
 link: ''
    });
    const { fetchApi } = useApi();
    const router = useRouter();

    onMounted(() => {
      achievementId.value = route.params.id;
      // In a real application, you would fetch the achievement data here
      // based on the achievementId to populate the form.
      // Example: fetchAchievement(achievementId.value).then(data => achievement.value = data);
      fetchAchievement();
    });

    const fetchAchievement = async () => {
      try {
        const response = await fetchApi(`/achievements/${achievementId.value}`, { method: 'GET' });
        achievement.value = response;
      } catch (error) {
        console.error('Error fetching achievement:', error);
        alert('Failed to fetch achievement.');
      }
    };

    const saveAchievement = async () => {
      if (!achievement.value.title || !achievement.value.description || achievement.value.difficulty === null) {
        alert('Please fill in all required fields.');
        return;
      }
      try {
        await fetchApi(`/achievements/${achievementId.value}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(achievement.value),
        });
        alert('Achievement updated successfully!');
      } catch (error) {
        console.error('Error saving achievement:', error);
        alert('Failed to save achievement.');
      }
    };

    return {
      achievementId,
      achievement,
      saveAchievement,
    };
  },
};
</script>

<style scoped>
.edit-achievement-view {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"],
textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>