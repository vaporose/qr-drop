<script setup lang="ts">
import { RouterView } from 'vue-router'
import Footer from './components/Footer.vue'
</script>

<template>
  <main class="min-h-screen min-w-screen">
    <div class="flex-grow">
      <RouterView />
    </div>
    <Footer />
  </main>
</template>

<style scoped>
/* Optional global styles here */
</style>
