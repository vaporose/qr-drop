<script setup lang="ts">
import { useSession } from '@/composables/useSession'

const { createSession } = useSession()
</script>

<template>
  <div class="flex flex-col items-center justify-center h-screen gap-4">
    <h1 class="text-3xl font-bold">{{ STRINGS.sessionExpired.title }}</h1>
    <p class="text-lg">{{ STRINGS.sessionExpired.message }}</p>
    <button @click="$router.push('/')" class="px-4 py-2 rounded-md">
      {{ STRINGS.sessionExpired.homeButton }}
    </button>
    <button @click="createSession()" class="px-4 py-2 rounded-md">
      Create New Chat
    </button>

  </div>
</template>

<style scoped>

</style>
