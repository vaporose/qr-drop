<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import { STRINGS } from '@/constants/strings'
import { MessageType } from '@/constants/enums'
import { CONFIG } from '@/constants/config'
import type { MessageSender, ChatMessage } from '@/constants/types'
import MessageList from '@/components/MessageList.vue'
import MessageInput from '@/components/MessageInput.vue'

const route = useRoute()
const identity = ref<string>('')
const sessionId = route.params.sessionId as string

const chatUrl = `${CONFIG.frontendUrl}/chat/${sessionId}`
const socket = ref<WebSocket | null>(null)

const messages = ref<ChatMessage[]>([])
const input = ref('')
const qrVisible = ref(true)

function handleSend(message: string) {
  if (socket.value) {
    socket.value.send(JSON.stringify({ type: 'chat_message', message }))
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

<template>
  <div class="min-h-screen p-6 flex flex-col items-center justify-start">
    <h2 class="text-2xl font-bold mb-4">{{ STRINGS.ui.chatRoomLabel }} {{ sessionId }}</h2>

    <!-- QR Code Section -->
    <div v-if="qrVisible" class="mb-6">
      <p class="text-sm text-gray-600 mb-2">{{ STRINGS.chat.scanPrompt }}</p>
      <QrcodeVue :value="chatUrl" :size="200" />
    </div>

    <!-- Chat Messages Section -->
    <MessageList :messages="messages" />

    <!-- Input Section -->
    <MessageInput @send="handleSend" />
  </div>
</template>

<style scoped>


</style>
