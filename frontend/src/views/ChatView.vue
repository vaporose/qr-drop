<template>
  <div class="min-h-screen p-6 flex flex-col items-center justify-start">
    <h2 class="text-2xl font-bold mb-4">{{ STRINGS.ui.chatRoomLabel }} {{ sessionId }}</h2>

    <!-- QR Code Section -->
    <div v-if="qrVisible" class="mb-6">
      <p class="text-sm text-gray-600 mb-2">{{ STRINGS.chat.scanPrompt }}</p>
      <QrcodeVue :value="chatUrl" :size="200" />
    </div>

    <!-- Chat Messages Section -->
    <div class="w-full max-w-xl rounded-md p-4 mb-4 h-64 overflow-y-auto chatbox">
      <div v-for="(msg, index) in messages" :key="index" class="mb-2">
        <div class="message-text px-3 py-2 rounded-md"
             :class="`message-${msg.sender}`">
          {{ msg.text }}
        </div>
        <div v-if="msg.sender !== 'system'" class="message-meta">
          <span class="message-identity">{{ msg.identity }}</span>
          <span class="message-actions">
            <!-- TODO: copy button etc go here -->
          </span>
        </div>
      </div>
    </div>

    <!-- Input Section -->
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
    socket.value.send(JSON.stringify({ type: 'chat_message', message: input.value }))
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
    } else if (data.type === MessageType.ChatMessage) {
      console.log('Received message', data)
      messages.value.push(
        data.client_id === identity.value
          ? { text: data.message, sender: 'self', identity: `This device: ${identity.value}` }
          : { text: data.message, sender: 'other', identity: data.client_id }
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

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  margin-left: 0.75rem;
  opacity: 0.6;
}

</style>
