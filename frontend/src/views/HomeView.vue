<script setup lang="ts">
import { useSession } from '@/composables/useSession'

const { createSession } = useSession()

</script>

<template>
  <div class="min-h-screen w-full flex flex-col items-center text-center px-4 justify-center gap-y-6">
    <h1 class="text-4xl font-bold mb-4">QR Drop</h1>
    <p class="text-lg mb-2">A quick and secure way to chat between devices.</p>
    <p class="text-sm mb-6 home-tagline">No logins. No tracking. Messages are never stored.</p>
    <button
      @click="createSession()"
      class="font-semibold py-3 px-6 rounded-lg text-xl transition"
    >
      Start New Chat
    </button>
  </div>
</template>

<style scoped>

.home-tagline {
  color: var(--color-text-muted);
}
</style>
