<template>
  <div class="min-h-screen p-6 flex flex-col items-center justify-start">
    <h2 class="text-2xl font-bold mb-4">Chat Room: {{ sessionId }}</h2>

    <div v-if="qrVisible" class="mb-6">
      <p class="text-sm text-gray-600 mb-2">Scan this QR code on another device to join:</p>
      <QrcodeVue :value="chatUrl" :size="200" />
    </div>

    <div class="w-full max-w-xl rounded-lg p-4 mb-4 h-64 overflow-y-auto">
      <div v-for="(msg, index) in messages" :key="index" class="mb-1">
        {{ msg }}
      </div>
    </div>

    <div class="w-full max-w-xl flex gap-2">
      <input
        v-model="input"
        @keyup.enter="sendMessage()"
        type="text"
        class="flex-grow px-4 py-2 border rounded-lg"
        placeholder="Type your message..."
      />
      <button @click="sendMessage()" class="px-4 py-2 rounded-lg">
        Send
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import { v4 as uuidv4 } from 'uuid'

const route = useRoute()
const clientId = uuidv4()
const sessionId = route.params.sessionId as string

const backendUrl = import.meta.env.VITE_BACKEND_URL
const frontendUrl = import.meta.env.VITE_FRONTEND_URL
const chatUrl = `${frontendUrl}/chat/${sessionId}`
const socket = ref<WebSocket | null>(null)
const messages = ref<string[]>([])
const input = ref('')
const qrVisible = ref(true)

function sendMessage() {

  if (socket.value && input.value.trim() !== '') {
    const payload = {
      client_id: clientId,
      message: input.value
    }
    console.log('Sending message...')
    socket.value.send(JSON.stringify(payload))
    input.value = ''
  }
}

onMounted(() => {
  socket.value = new WebSocket(`ws://${backendUrl}/ws/${sessionId}`)

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'user_joined') {
      const userCount = data.count
      if (userCount >= 2) {
        qrVisible.value = false  // Hides the QR code
      }
    } else {
      messages.value.push(
        data.client_id === clientId
          ? `You: ${data.message}`
          : `Them: ${data.message}`
      )
    }


  }

  socket.value.onopen = () => {
    messages.value.push('[Connected]')
  }

  socket.value.onclose = () => {
    messages.value.push('[Disconnected]')
  }
})

onUnmounted(() => {
  socket.value?.close()
})
</script>


