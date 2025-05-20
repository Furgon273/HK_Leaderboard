<template>
  <v-app-bar app color="primary" class="menu">
    <v-toolbar-title>HK Leaderboard</v-toolbar-title>
    <v-spacer></v-spacer>
    
    <div class="nav-buttons">
      <v-btn to="/" text class="nav-btn">Главная</v-btn>
      <v-btn to="/leaderboard" text class="nav-btn">Топ игроков</v-btn>
      <v-btn
          v-if="authStore.user?.role === 'admin'"
          to="/admin"
          text
          class="nav-btn"
          >
          Админ-панель
      </v-btn>

      <template v-if="!authStore.isAuthenticated">
        <v-btn to="/login" text class="nav-btn">Войти</v-btn>
        <v-btn to="/register" text class="nav-btn">Регистрация</v-btn>
      </template>

      <template v-else>
        <v-btn to="/submit-run" text class="nav-btn">Добавить забег</v-btn>
        <v-btn :to="`/profile/${authStore.user.username}`" text class="nav-btn">
          <v-icon left>mdi-account</v-icon>
          {{ authStore.user.username }}
        </v-btn>
        <v-btn @click="authStore.logout()" text class="nav-btn">Выйти</v-btn>
      </template>
    </div>
  </v-app-bar>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
const authStore = useAuthStore()
</script>