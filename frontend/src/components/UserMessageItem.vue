<script setup lang="ts">
import type { UserMessage } from '../models/conversation'
defineProps<{ item: UserMessage }>()
</script>

<template>
  <div class="user-message">
    <div class="msg-wrap">
      <div class="bubble">{{ item.content }}</div>
      <time class="timestamp">{{ new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</time>
    </div>
  </div>
</template>

<style scoped>
.user-message {
  display: flex;
  justify-content: flex-end;
  margin: 8px 0;
}
.msg-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  max-width: 70%;
}
.bubble {
  background: #c64500;
  color: #ffffff;
  padding: 10px 16px;
  border-radius: 18px 18px 4px 18px;
  line-height: 1.5;
  word-break: break-word;
}
.timestamp {
  font-size: 0.7rem;
  color: #bbb;
  margin-top: 3px;
  font-style: normal;
}
</style>
