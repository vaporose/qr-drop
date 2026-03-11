<template>
  <div class="min-h-screen p-6 flex flex-col items-center justify-start">
    <h2 class="text-2xl font-bold mb-4">{{ STRINGS.ui.chatRoomLabel }} {{ sessionId }}</h2>

    <div v-if="qrVisible" class="mb-6">
      <p class="text-sm text-gray-600 mb-2">{{ STRINGS.chat.scanPrompt }}</p>
      <QrcodeVue :value="chatUrl" :size="200" />
    </div>

    <div class="w-full max-w-xl rounded-md p-4 mb-4 h-64 overflow-y-auto chatbox">
      <div v-for="(msg, index) in messages" :key="index"
        class="mb-1 px-3 py-1 rounded-md"
        :class="`message-${msg.sender}`"
      >
        {{ msg.text }}
      </div>
    </div>

    <div class="w-full max-w-xl flex gap-2">
      <input
        v-model="input"
        @keyup.enter="sendMessage()"
        type="text"
        class="flex-grow px-4 py-2 border rounded-md messagebox"
        :placeholder="STRINGS.chat.placeholder"
      />
      <button @click="sendMessage()" class="px-4 py-2 rounded-md">
        {{ STRINGS.chat.sendButton }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import { STRINGS } from '@/constants/strings'
import { MessageType } from '@/constants/enums'
import { CONFIG } from '@/constants/config'

const route = useRoute()
const identity = ref<string>('')
const sessionId = route.params.sessionId as string

const chatUrl = `${CONFIG.frontendUrl}/chat/${sessionId}`
const socket = ref<WebSocket | null>(null)
type MessageSender = 'self' | 'other' | 'system'

const messages = ref<{ text: string; sender: MessageSender }[]>([])
const input = ref('')
const qrVisible = ref(true)

function sendMessage() {
  if (socket.value && input.value.trim() !== '') {
    socket.value.send(JSON.stringify(input.value))
    input.value = ''
  }
}

onMounted(() => {
  socket.value = new WebSocket(`${CONFIG.backendWsUrl}/${sessionId}`)

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === MessageType.UserJoined) {
      if (!identity.value) {
        identity.value = data.identity
      }
      if (data.count >= 2) {
        qrVisible.value = false
      }
    } else {
      console.log('Received message', data)
      messages.value.push(
        data.client_id === identity.value
          ? { text: `${STRINGS.chat.you}: ${data.message}`, sender: 'self' }
          : { text: `${data.client_id}: ${data.message}`, sender: 'other' }
      )
    }
  }

  socket.value.onopen = () => {
    messages.value.push({ text: STRINGS.chat.connected, sender: "system" })
  }

  socket.value.onclose = () => {
    messages.value.push({ text: STRINGS.chat.disconnected, sender: "system" })
  }
})

onUnmounted(() => {
  socket.value?.close()
})
</script>

<style scoped>
.chatbox {
  background-color: var(--color-background-soft);
}

.messagebox {
  background-color: var(--color-background-mute);
}

.message-self{
  background-color: var(--color-background-accent);
}

.message-other{
  background-color: var(--color-background-transparent);
}

.message-system {
  background-color: transparent;
  text-align: center;
  font-style: italic;
  color: var(--color-text-mute);
}

</style>
