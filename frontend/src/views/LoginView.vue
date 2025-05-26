<template>
  <v-container class="fill-height">
    <v-card class="pa-4">
      <v-card-title class="text-center">Вход</v-card-title>
      <v-card-text>
        <v-alert
          v-if="loginError"
          type="error"
          class="mb-4"
        >
          {{ loginError }}
        </v-alert>
        <v-form @submit.prevent="handleLogin">
          <v-text-field
            v-model="username"
            label="Никнейм"
            required
          ></v-text-field>
          
          <v-text-field
            v-model="password"
            label="Пароль"
            type="password"
            required
          ></v-text-field>
          
          <v-btn 
            type="submit" 
            color="primary" 
            block 
            :loading="loading"
            size="large"
          >
            Войти
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const loginError = ref(null);
const error = ref(null)

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  try {
    loading.value = true;
    loginError.value = null; // Reset error message
    const success = await authStore.login(username.value, password.value)
    if (success) {
      router.push('/')
    }
  } catch (err) {
    console.log("Entering catch block with error:", err);
    console.error("Login error:", err);
    console.log("Full error object:", err);
    console.log("Error response:", err.response);
    console.log("Error response data:", err.response ? err.response.data : 'No response data');
    console.log("Error message from data:", err.response && err.response.data ? err.response.data.message : 'No message in response data');
    if (err.response && err.response.data && err.response.data.msg) {
      loginError.value = err.response.data.msg;
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
  .v-card {
    background-color: var(--color-background);
    width: 300px;
  }
  .v-text-field {
    background-color: var(--color-background);
    color: var(--color-text);
  }
  .v-container {
    width: 600%; 
  }
</style>