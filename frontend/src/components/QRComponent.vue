<script setup lang="ts">
import QrcodeVue from 'qrcode.vue'
import { STRINGS } from '@/constants/strings'
import { CONFIG } from '@/constants/config'

const props = defineProps<{
  sessionId: string
  qrVisible: boolean
}>()

const chatUrl = `${CONFIG.frontendUrl}/chat/${sessionId}`

</script>

<template>
    <div class="md:w-64 md:flex-shrink-0 flex flex-col items-center">
      <h2 class="text-2xl font-bold mb-4">{{ STRINGS.ui.chatRoomLabel }} {{ sessionId }}</h2>
      <div v-if="qrVisible">
        <p class="text-sm text-gray-600 mb-2">{{ STRINGS.chat.scanPrompt }}</p>
        <QrcodeVue :value="chatUrl" :size="200" />
      </div>
      <button @click="goHome" class="mt-4">{{ STRINGS.ui.homeButton }}</button>
    </div>
</template>

<style scoped>

</style>
