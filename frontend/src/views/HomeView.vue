<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const backendUrl = import.meta.env.VITE_BACKEND_URL
const protocol = import.meta.env.VITE_URL_PROTOCOL

async function createSession() {
  try {
    const response = await fetch(`${protocol}://${backendUrl}/create-session`, {
      method: 'POST'
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    await router.push(`/chat/${data.session_id}`)
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}
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
