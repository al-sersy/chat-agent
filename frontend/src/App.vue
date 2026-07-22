<script setup lang="ts">
import { ref } from 'vue'
import { sendMessage } from './api/chatApi'
import type { ConversationItem } from './models/conversation'
import ConversationList from './components/ConversationList.vue'
import ChatComposer from './components/ChatComposer.vue'

const items = ref<ConversationItem[]>([])
const loading = ref(false)
const networkError = ref<string | null>(null)

async function handleSend(message: string) {
  loading.value = true
  networkError.value = null
  try {
    items.value = await sendMessage(message)
  } catch (err) {
    networkError.value = err instanceof Error ? err.message : 'Network error — please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app">
    <header class="header">
      <h1>Chat Agent</h1>
    </header>

    <ConversationList :items="items" />

    <div v-if="networkError" class="network-error">
      {{ networkError }}
    </div>

    <ChatComposer :loading="loading" @send="handleSend" />
  </div>
</template>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: #ffffff;
}
.header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: #ffd900;
  color: #1a1a1a;
  flex-shrink: 0;
}
.logo {
  font-size: 1.1rem;
}
.header h1 {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.network-error {
  padding: 8px 16px;
  background: #fff5f5;
  border-top: 2px solid #e53935;
  color: #c62828;
  font-size: 0.85rem;
  flex-shrink: 0;
}
</style>
