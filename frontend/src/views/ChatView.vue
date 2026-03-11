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
import { v4 as uuid4 } from 'uuid'
import { STRINGS } from '@/constants/strings'
import { MessageType } from '@/constants/enums'
import { CONFIG } from '@/constants/config'

const route = useRoute()
const clientId = uuid4()
const sessionId = route.params.sessionId as string

const chatUrl = `${CONFIG.frontendUrl}/chat/${sessionId}`
const socket = ref<WebSocket | null>(null)
type MessageSender = 'self' | 'other' | 'system'

const messages = ref<{ text: string; sender: MessageSender }[]>([])
const input = ref('')
const qrVisible = ref(true)

function sendMessage() {
  if (socket.value && input.value.trim() !== '') {
    const payload = {
      client_id: clientId,
      message: input.value
    }
    console.log('Sending message')
    socket.value.send(JSON.stringify(payload))
    input.value = ''
  }
}

onMounted(() => {
  socket.value = new WebSocket(`${CONFIG.backendWsUrl}/${sessionId}`)

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === MessageType.UserJoined) {
      if (data.count >= 2) {
        qrVisible.value = false
      }
    } else {
      messages.value.push(
        data.client_id === clientId
          ? { text: `${STRINGS.chat.you}: ${data.message}`, self: true }
          : { text: `${STRINGS.chat.them}: ${data.message}`, self: false }
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
