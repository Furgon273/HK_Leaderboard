<template>
  <v-app-bar app color="primary">
    <v-app-bar-nav-icon class="hidden-md-and-up" @click="drawer = !drawer"></v-app-bar-nav-icon>
    <v-toolbar-title>HK Leaderboard</v-toolbar-title>
    <v-spacer></v-spacer>
    
    <div class="hidden-sm-and-down">
      <v-btn to="/leaderboard" text>Топ игроков</v-btn>
      <v-btn
        v-if="authStore.user?.role === 'admin'"
        to="/admin"
        text
        >
        Админ-панель
      </v-btn>

      <template v-if="!authStore.isAuthenticated">
        <v-btn to="/login" text>Войти</v-btn>
        <v-btn to="/register" text>Регистрация</v-btn>
      </template>

      <template v-else>
        <v-btn :to="`/profile/${authStore.user.username}`" text>
          <v-icon left>mdi-account</v-icon>
          {{ authStore.user.username }}
        </v-btn>
        <v-btn @click="authStore.logout()" text>Выйти</v-btn>
      </template>
    </div>
  </v-app-bar>
  <v-navigation-drawer v-model="drawer" app temporary>
    <v-list dense>
      <v-list-item to="/leaderboard">
        <v-list-item-title>Топ игроков</v-list-item-title>
      </v-list-item>

      <v-list-item v-if="authStore.user?.role === 'admin'" to="/admin">
        <v-list-item-title>Админ-панель</v-list-item-title>
      </v-list-item>

      <template v-if="!authStore.isAuthenticated">
        <v-list-item to="/login">
          <v-list-item-title>Войти</v-list-item-title>
        </v-list-item>
        <v-list-item to="/register">
          <v-list-item-title>Регистрация</v-list-item-title>
        </v-list-item>
      </template>
      <template v-else>
        <v-list-item :to="`/profile/${authStore.user.username}`"><v-list-item-title>Профиль</v-list-item-title></v-list-item>
        <v-list-item @click="authStore.logout()"><v-list-item-title>Выйти</v-list-item-title></v-list-item>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { ref } from 'vue'
const authStore = useAuthStore()
const drawer = ref(false)
</script>