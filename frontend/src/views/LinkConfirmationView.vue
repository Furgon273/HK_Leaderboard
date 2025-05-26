<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card class="pa-6 text-center" max-width="400">
      <v-card-title class="headline">Предупреждение о переходе</v-card-title>
      <v-card-text>
        <p>Вы собираетесь покинуть этот сайт и перейти по внешней ссылке:</p>
        <p class="font-weight-bold">{{ targetUrl }}</p>
        <p class="mt-4">Продолжить?</p>
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="red darken-1" text @click="cancelRedirect">Отмена</v-btn>
        <v-btn color="green darken-1" text @click="confirmRedirect">Продолжить</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const targetUrl = ref('');

onMounted(() => {
  // Get the target URL from the route query parameters
  targetUrl.value = route.query.url || 'Неизвестная ссылка';
});

const confirmRedirect = () => {
  // Redirect to the external URL
  window.location.href = targetUrl.value;
};

const cancelRedirect = () => {
  // Go back to the previous page
  router.go(-1);
};
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
</style>