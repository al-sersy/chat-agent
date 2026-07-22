<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ loading: boolean }>()
const emit = defineEmits<{ send: [message: string] }>()

const text = ref('')

function submit() {
  const message = text.value.trim()
  if (!message) return
  emit('send', message)
  text.value = ''
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    submit()
  }
}
</script>

<template>
  <div class="composer">
    <textarea
      v-model="text"
      :disabled="loading"
      placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
      rows="1"
      class="input"
      @keydown="onKeydown"
    />
    <button
      :disabled="loading || !text.trim()"
      class="send-btn"
      @click="submit"
    >
      <span v-if="loading" class="btn-spinner" aria-hidden="true" />
      <span v-else>Send</span>
    </button>
  </div>
</template>

<style scoped>
.composer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 2px solid #ffd900;
  background: #ffffff;
}
.input {
  flex: 1;
  resize: none;
  padding: 10px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 0.95rem;
  font-family: inherit;
  line-height: 1.5;
  outline: none;
  transition: border-color 0.15s;
  background: #ffffff;
  color: #1a1a1a;
}
.input:focus {
  border-color: #ffd900;
}
.input:disabled {
  background: #fafafa;
  color: #999;
}
.send-btn {
  padding: 0 22px;
  background: #ffd900;
  color: #1a1a1a;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
  min-width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.send-btn:hover:not(:disabled) {
  background: #f0ca00;
}
.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #1a1a1a;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
