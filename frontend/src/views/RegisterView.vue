<template>
  <v-container class="fill-height">
    <v-card class="pa-4">
      <v-card-title class="text-center">Регистрация</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="handleRegister">
          <v-text-field
            v-model="form.username"
            label="Никнейм"
            :error-messages="errors.username"
            required
            outlined
          ></v-text-field>
          
          <v-text-field
            v-model="form.email"
            label="Email"
            type="email"
            :error-messages="errors.email"
            required
            outlined
          ></v-text-field>
          
          <v-text-field
            v-model="form.password"
            label="Пароль"
            type="password"
            :error-messages="errors.password"
            required
            outlined
          ></v-text-field>
          
          <v-text-field
            v-model="form.password_confirmation"
            label="Подтверждение пароля"
            type="password"
            :error-messages="errors.password_confirmation"
            required
            outlined
          ></v-text-field>
          
          <v-btn 
            type="submit" 
            color="primary" 
            block 
            :loading="loading"
            size="large"
          >
            Зарегистрироваться
          </v-btn>
          
          <div class="text-center mt-4">
            Уже есть аккаунт? <router-link to="/login">Войти</router-link>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'

const router = useRouter()
const { fetchApi } = useApi()

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirmation: ''
})

const errors = ref({})
const loading = ref(false)

const validate = () => {
  errors.value = {}
  let valid = true

  if (!form.value.username) {
    errors.value.username = 'Введите никнейм'
    valid = false
  }

  if (!form.value.email) {
    errors.value.email = 'Введите email'
    valid = false
  } else if (!/^\S+@\S+\.\S+$/.test(form.value.email)) {
    errors.value.email = 'Введите корректный email'
    valid = false
  }

  if (!form.value.password) {
    errors.value.password = 'Введите пароль'
    valid = false
  } else if (form.value.password.length < 6) {
    errors.value.password = 'Пароль должен быть не менее 6 символов'
    valid = false
  }

  if (form.value.password !== form.value.password_confirmation) {
    errors.value.password_confirmation = 'Пароли не совпадают'
    valid = false
  }

  return valid
}

const handleRegister = async () => {
  if (!validate()) return

  loading.value = true
  errors.value = {}

  try {
    await fetchApi('/register', {
      method: 'POST',
      body: JSON.stringify(form.value),
    })
    
    router.push('/login')
  } catch (error) {
    console.log("Caught error:", error); // Log 1: Пойманная ошибка

    if (error.response && error.response.data) {
      if (error.response.data.message) {
        console.log("Error message found:", error.response.data.message); // Log 2: Найденное сообщение

        const errorMessage = error.response.data.message;

        // Попытка привязать ошибки к полям формы на основе текста сообщения
        if (errorMessage.includes('именем уже существует')) {
          errors.value.username = errorMessage;
          console.log("Username error set:", errors.value.username); // Log 3: Установлена ошибка никнейма
        } else if (errorMessage.includes('email уже существует')) {
          errors.value.email = errorMessage;
          console.log("Email error set:", errors.value.email); // Log 3: Установлена ошибка email
        } else {
          // Для других ошибок (отсутствие полей, ошибка сервера и т.д.)
          // Пока просто выведем их в консоль.
          console.error("Backend Error:", errorMessage);
        }
      } else if (error.response.data.errors) {
         console.log("Backend errors field found:", error.response.data.errors);
         errors.value = error.response.data.errors;
      } else {
        console.error("API call failed or unexpected error format:", error);
        console.error("Unexpected backend error format:", error.response.data);
      }
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.v-card {
  background-color: var(--card-bg);
  color: var(--text-color);
  border-radius: 8px;
  border: 1px solid #333;
}

.v-card-title {
  color: var(--accent-color);
  font-weight: 500;
  padding-bottom: 10px;
  border-bottom: 1px solid #333;
}

.v-text-field,
.v-text-field .v-label,
.v-text-field input {
  color: var(--text-color);
}

.v-text-field .v-input__control {
  background-color: #252525;
}

a {
  color: var(--hover-color);
  text-decoration: none;
}
</style>