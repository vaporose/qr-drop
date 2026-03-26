<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { STRINGS } from '@/constants/strings'
import { MessageType } from '@/constants/enums'
import { ENDPOINTS } from '@/constants/endpoints'
import type { MessageSender, ChatMessage } from '@/constants/types'
import MessageList from '@/components/MessageList.vue'
import MessageInput from '@/components/MessageInput.vue'
import QRComponent from '@/components/QRComponent.vue'

const route = useRoute()
const router = useRouter()
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
  socket.value = new WebSocket(ENDPOINTS.connections.chat(sessionId));

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === MessageType.UserJoined) {
      if (!identity.value) {
        identity.value = data.identity.unique_identifier
      }
      if (data.count >= 2) {
        qrVisible.value = false
      }
    } else if (data.type === MessageType.ChatMessage) {
      messages.value.push(
        data.identity.unique_identifier === identity.value
          ? { content: data.content, created_at: data.created_at, sender_type: 'self', identity: data.identity }
          : { content: data.content, created_at: data.created_at, sender_type: 'other', identity: data.identity }
      )
    }
  }

  socket.value.onopen = () => {
    messages.value.push({ content: STRINGS.chat.connected, sender_type: "system" })
  }

  socket.value.onclose = async (event) => {
    if (event.code === 4004) {
      await router.push('/session-expired')
    } else {
      messages.value.push({ content: STRINGS.chat.disconnected, sender_type: "system" })
    }
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
