<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { streamMessage } from './api/chatApi'
import type { ConversationItem } from './models/conversation'
import ConversationList from './components/ConversationList.vue'
import ChatComposer from './components/ChatComposer.vue'

const STORAGE_KEY = 'chatItems'

const items = ref<ConversationItem[]>([])
const loading = ref(false)
const networkError = ref<string | null>(null)
const lastMessage = ref('')

onMounted(() => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) items.value = JSON.parse(saved)
  } catch { /* ignore corrupt storage */ }
})

let saveTimer: ReturnType<typeof setTimeout> | null = null
watch(items, (val) => {
  if (saveTimer) clearTimeout(saveTimer)
  // debounce to avoid a write on every streamed item
  saveTimer = setTimeout(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(val)) }, 200)
}, { deep: true })

function newChat() {
  items.value = []
  networkError.value = null
  localStorage.removeItem(STORAGE_KEY)
}

async function handleSend(message: string) {
  lastMessage.value = message
  loading.value = true
  networkError.value = null
  try {
    for await (const item of streamMessage(message)) {
      items.value = [...items.value, item]
      if (item.type === 'tool_call') {
        await new Promise<void>(resolve => setTimeout(resolve, 200))
      }
    }
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
      <img src="/logo.png" alt="Chat Agent" class="header-logo" />
      <button class="new-chat-btn" :disabled="loading" @click="newChat">New chat</button>
    </header>

    <ConversationList :items="items" :loading="loading" />

    <div v-if="networkError" class="network-error">
      <span>{{ networkError }}</span>
      <button class="retry-btn" @click="handleSend(lastMessage)">Retry</button>
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
  height: 70px;
  padding: -0px 20px;
  background: #ffffff;
  border-bottom: 3px solid #c64500;
  flex-shrink: 0;
}
.header-logo {
  height: 140%;
  width: auto;
  object-fit: contain;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 16px;
  background: #fff5f5;
  border-top: 2px solid #e53935;
  color: #c62828;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.new-chat-btn {
  margin-left: auto;
  background: transparent;
  border: 1.5px solid #c64500;
  color: #c64500;
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
}
.new-chat-btn:hover:not(:disabled) { background: rgba(198, 69, 0, 0.08); }
.new-chat-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.retry-btn {
  background: #e53935;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.retry-btn:hover { background: #c62828; }
@media (max-width: 600px) {
  .app { max-width: 100%; }
  .header { padding: 10px 12px; }
}
</style>
