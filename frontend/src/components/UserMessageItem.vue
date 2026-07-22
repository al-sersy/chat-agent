<script setup lang="ts">
import type { UserMessage } from '../models/conversation'
defineProps<{ item: UserMessage }>()
</script>

<template>
  <div class="user-message">
    <div class="bubble">{{ item.content }}</div>
  </div>
</template>

<style scoped>
.user-message {
  display: flex;
  justify-content: flex-end;
  margin: 8px 0;
}
.bubble {
  background: #ffd900;
  color: #1a1a1a;
  padding: 10px 16px;
  border-radius: 18px 18px 4px 18px;
  max-width: 70%;
  line-height: 1.5;
  word-break: break-word;
}
</style>
