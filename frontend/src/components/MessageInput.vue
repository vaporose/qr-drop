<script setup lang="ts">
import { STRINGS } from '@/constants/strings'
import { ref } from 'vue'

const emit = defineEmits<{
  send: [message: string]
}>()

const input = ref('')

function sendMessage() {
  if (input.value.trim() !== '') {
    emit('send', input.value)
    input.value = ''
  }
}


</script>

<template>
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
</template>

<style scoped>
  .messagebox {
    background-color: var(--color-background-mute);
  }
</style>
