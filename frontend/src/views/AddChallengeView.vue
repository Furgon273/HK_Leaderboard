<template>
  <div class="container">
    <h1>Add New Challenge</h1>
    <form @submit.prevent="handleSubmit" class="challenge-form">
      <div class="form-group">
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="name" required>
      </div>

      <div class="form-group">
        <label for="description">Description:</label>
        <textarea id="description" v-model="description" rows="5" required></textarea>
      </div>

      <div class="form-group">
        <label for="difficulty">Difficulty:</label>
        <input type="number" id="difficulty" v-model="difficulty" required min="1">
      </div>

      <div class="form-group">
        <label for="league">League:</label>
        <input type="text" id="league" v-model="league" required>
      </div>

      <button type="submit" class="submit-button">Add Challenge</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter for redirection
import { useApi } from '@/composables/useApi'; // Import useApi

const router = useRouter();
const name = ref('');
const description = ref('');
const difficulty = ref(null);
const league = ref('');

const handleSubmit = () => {
  console.log('Form submitted!');
  const newChallengeData = {
    name: name.value,
    description: description.value,
    difficulty: difficulty.value,
    league: league.value,
  };

  console.log('Submitting challenge data:', newChallengeData);

  const { fetchApi } = useApi(); // Get fetchApi from the composable
  fetchApi('/challenges', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newChallengeData),
  })
    .then(response => {
      console.log('Challenge creation response:', response);
      router.push({ name: 'AdminPanel' });
    })
    .catch(error => {
      console.error('Error creating challenge:', error);
      alert('Failed to create challenge.');
    });
};
</script>

<style scoped>
.container {
  background-color: var(--card-bg);
  color: var(--text-color);
  max-width: 600px;
 margin: 40px auto;
 padding: 20px;
  border-radius: 8px;
  border: 1px solid #333;
}

h1 {
  text-align: center;
  color: var(--accent-color);
  margin-bottom: 20px;
  font-weight: 500;
}

.challenge-form .form-group {
 margin-bottom: 15px;
}

.challenge-form input[type="text"],
.challenge-form input[type="number"],
.challenge-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #555;
  border-radius: 4px;
  background-color: #252525;
  color: var(--text-color);
  box-sizing: border-box;
}

.challenge-form input[type="number"] {
 -moz-appearance: textfield; /* Remove default number input arrows in Firefox */
}
.challenge-form input[type="number"]::-webkit-outer-spin-button,
.challenge-form input[type="number"]::-webkit-inner-spin-button {
 -webkit-appearance: none; /* Remove default number input arrows in Chrome, Safari, Edge */
    margin: 0;
}


.challenge-form textarea {
  resize: vertical; /* Allow vertical resizing */
  font-family: inherit;
}

.submit-button {
  display: block;
  width: 100%;
  padding: 10px;
  background-color: var(--hover-color);
  color: var(--text-color);
  border-color: var(--vt-c-black-soft);
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
</style>