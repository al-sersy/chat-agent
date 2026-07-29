<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from '../lib/markdown'
import DOMPurify from 'dompurify'
import type { AssistantMessage } from '../models/conversation'

const props = defineProps<{ item: AssistantMessage }>()

const copied = ref(false)

const sanitizedMarkdown = computed(() =>
  DOMPurify.sanitize(marked.parse(props.item.content) as string)
)

async function copyText() {
  await navigator.clipboard.writeText(props.item.content)
  copied.value = true
  setTimeout(() => { copied.value = false }, 1500)
}
</script>

<template>
  <div class="assistant-message">
    <div class="msg-wrap">
      <div class="bubble-wrap">
        <div class="bubble" v-html="sanitizedMarkdown" />
        <button class="copy-btn" :aria-label="copied ? 'Copied' : 'Copy'" @click="copyText">{{ copied ? '✓' : '⎘' }}</button>
      </div>
      <time class="timestamp">{{ new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</time>
    </div>
  </div>
</template>

<style scoped>
.assistant-message {
  display: flex;
  justify-content: flex-start;
  margin: 8px 0;
}
.msg-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 70%;
}
.bubble-wrap {
  position: relative;
  width: 100%;
}
.bubble {
  background: #f8f8f8;
  color: #1a1a1a;
  padding: 10px 36px 10px 16px;
  border-radius: 18px 18px 18px 4px;
  border-left: 3px solid #e08000;
  line-height: 1.5;
  word-break: break-word;
}
.timestamp {
  font-size: 0.7rem;
  color: #bbb;
  margin-top: 3px;
  font-style: normal;
}
.bubble :deep(p) { margin: 0.4em 0; }
.bubble :deep(p:first-child) { margin-top: 0; }
.bubble :deep(p:last-child) { margin-bottom: 0; }
.bubble :deep(code) {
  background: rgba(0,0,0,0.07);
  border-radius: 3px;
  padding: 1px 4px;
  font-size: 0.88em;
  font-family: ui-monospace, monospace;
}
.bubble :deep(pre) {
  background: rgba(0,0,0,0.07);
  border-radius: 6px;
  padding: 10px;
  overflow-x: auto;
  font-size: 0.85em;
  margin: 0.5em 0;
}
.bubble :deep(pre code) { background: none; padding: 0; }
.bubble :deep(ul), .bubble :deep(ol) { margin: 0.4em 0; padding-left: 1.5em; }
.bubble :deep(h1), .bubble :deep(h2), .bubble :deep(h3) {
  margin: 0.5em 0 0.2em;
  font-size: 1em;
  font-weight: 700;
}
.bubble :deep(a) { color: #1565c0; }
.bubble :deep(table) { border-collapse: collapse; width: 100%; margin: 0.5em 0; font-size: 0.9em; }
.bubble :deep(th), .bubble :deep(td) { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
.bubble :deep(tr:nth-child(even)) { background: rgba(0,0,0,0.03); }
.bubble :deep(th) { background: rgba(0,0,0,0.05); font-weight: 600; }
.copy-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #bbb;
  padding: 2px 5px;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.15s, background 0.15s;
}
.copy-btn:hover { color: #555; background: rgba(0,0,0,0.06); }
</style>
