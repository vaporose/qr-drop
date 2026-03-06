<script setup lang="ts">
import { ref } from 'vue'

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="w-full border-t border-gray-400 px-4 py-3">
    <div class="flex flex-col items-center justify-between gap-2 sm:flex-row">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        <p>&copy; {{ currentYear }} Chaila Erie. All rights reserved.</p>
      </div>
      <div class="text-sm text-gray-600 dark:text-gray-400">
        <slot name="funding"></slot>
      </div>
    </div>
  </footer>
</template>

<style scoped>

</style>
