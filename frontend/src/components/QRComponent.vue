<script setup lang="ts">
import QrcodeVue from 'qrcode.vue'
import { STRINGS } from '@/constants/strings'
import { CONFIG } from '@/constants/config'
import { useEndSession } from '@/composables/endSession.ts'

const props = defineProps<{
  sessionId: string
  qrVisible: boolean
}>()

const chatUrl = `${CONFIG.frontendUrl}/chat/${props.sessionId}`
const { endSession } = useEndSession()

</script>

<template>
    <div class="md:w-64 md:flex-shrink-0 flex flex-col items-center">
      <h2 class="text-2xl font-bold mb-4">{{ STRINGS.ui.chatRoomLabel }} {{ props.sessionId }}</h2>
      <div v-if="props.qrVisible">
        <p class="text-sm text-gray-600 mb-2">{{ STRINGS.chat.scanPrompt }}</p>
        <QrcodeVue :value="chatUrl" :size="200" class="ml-4"/>
      </div>
      <button
          @click="endSession(props.sessionId)"
          class="button-destructive font-semibold py-3 px-6 rounded-lg m-4 transition">
        {{ STRINGS.ui.terminate }}
      </button>
    </div>
</template>

<style scoped>

</style>
