<template>
  <v-app>
    <NavBar />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
</script>
<style>
#app {
  display: flex;
  justify-content: center;
  overflow-x: hidden;
}
</style>