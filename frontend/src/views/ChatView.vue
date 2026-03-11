<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { STRINGS } from '@/constants/strings'
import { MessageType } from '@/constants/enums'
import { CONFIG } from '@/constants/config'
import type { MessageSender, ChatMessage } from '@/constants/types'
import MessageList from '@/components/MessageList.vue'
import MessageInput from '@/components/MessageInput.vue'
import QRComponent from '@/components/QRComponent.vue'

const route = useRoute()
const identity = ref<string>('')
const sessionId = route.params.sessionId as string
const socket = ref<WebSocket | null>(null)
const messages = ref<ChatMessage[]>([])
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
  <div class="min-h-screen p-6 flex flex-col md:flex-row gap-6">

    <!-- Left column: title, QR, help -->
    <QRComponent :sessionId="sessionId" :qrVisible="qrVisible" />

    <!-- Right column: chat -->
    <div class="flex flex-col flex-grow">
      <MessageList :messages="messages" />
      <MessageInput @send="handleSend" />
    </div>

  </div>
</template>

<style scoped>


</style>
