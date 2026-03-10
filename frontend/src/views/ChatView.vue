<template>
  <div class="min-h-screen p-6 flex flex-col items-center justify-start">
    <h2 class="text-2xl font-bold mb-4">{{ STRINGS.ui.chatRoomLabel }} {{ sessionId }}</h2>

    <div v-if="qrVisible" class="mb-6">
      <p class="text-sm text-gray-600 mb-2">{{ STRINGS.chat.scanPrompt }}</p>
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
        :placeholder="STRINGS.chat.placeholder"
      />
      <button @click="sendMessage()" class="px-4 py-2 rounded-lg">
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
const messages = ref<string[]>([])
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
          ? `${STRINGS.chat.you}: ${data.message}`
          : `${STRINGS.chat.them}: ${data.message}`
      )
    }
  }

  socket.value.onopen = () => {
    messages.value.push(STRINGS.chat.connected)
  }

  socket.value.onclose = () => {
    messages.value.push(STRINGS.chat.disconnected)
  }
})

onUnmounted(() => {
  socket.value?.close()
})
</script>
