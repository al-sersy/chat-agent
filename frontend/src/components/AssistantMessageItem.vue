<script setup lang="ts">
import type { AssistantMessage } from '../models/conversation'
defineProps<{ item: AssistantMessage }>()
</script>

<template>
  <div class="assistant-message">
    <div class="bubble">{{ item.content }}</div>
  </div>
</template>

<style scoped>
.assistant-message {
  display: flex;
  justify-content: flex-start;
  margin: 8px 0;
}
.bubble {
  background: #f8f8f8;
  color: #1a1a1a;
  padding: 10px 16px;
  border-radius: 18px 18px 18px 4px;
  border-left: 3px solid #ffd900;
  max-width: 70%;
  line-height: 1.5;
  word-break: break-word;
}
</style>
