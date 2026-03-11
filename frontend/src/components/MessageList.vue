<script setup lang="ts">
import type { ChatMessage } from '@/constants/types'

const props = defineProps<{
  messages: ChatMessage[]
}>()

</script>

<template>
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
</template>

<style scoped>
.chatbox {
  background-color: var(--color-background-soft);
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
