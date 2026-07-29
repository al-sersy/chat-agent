<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import type { ConversationItem, ToolResult, ToolCall } from '../models/conversation'
import UserMessageItem from './UserMessageItem.vue'
import AssistantMessageItem from './AssistantMessageItem.vue'
import ToolCallItem from './ToolCallItem.vue'
import ToolResultItem from './ToolResultItem.vue'
import ErrorItem from './ErrorItem.vue'
import ThinkingItem from './ThinkingItem.vue'

const props = defineProps<{ items: ConversationItem[]; loading: boolean }>()

// maps tool_call_id → { status, duration } once a matching tool_result arrives
const toolCallInfo = computed(() => {
  const callTimes: Record<string, string> = {}
  const info: Record<string, { status: 'success' | 'error'; duration?: string }> = {}
  for (const item of props.items) {
    if (item.type === 'tool_call') {
      callTimes[(item as ToolCall).tool_call_id] = (item as ToolCall).timestamp
    } else if (item.type === 'tool_result') {
      const tr = item as ToolResult
      const start = callTimes[tr.tool_call_id]
      let duration: string | undefined
      if (start) {
        const ms = new Date(tr.timestamp).getTime() - new Date(start).getTime()
        duration = ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`
      }
      info[tr.tool_call_id] = { status: 'success', duration }
    }
  }
  return info
})

const container = ref<HTMLElement | null>(null)
const showScrollBtn = ref(false)

function onScroll() {
  if (!container.value) return
  const { scrollTop, scrollHeight, clientHeight } = container.value
  showScrollBtn.value = scrollHeight - scrollTop - clientHeight > 120
}

function scrollToBottom() {
  if (!container.value) return
  container.value.scrollTop = container.value.scrollHeight
  showScrollBtn.value = false
}

watch(
  () => props.items.length,
  async () => {
    if (!container.value) return
    const { scrollTop, scrollHeight, clientHeight } = container.value
    const wasNearBottom = scrollHeight - scrollTop - clientHeight < 120
    await nextTick()
    if (wasNearBottom && container.value) {
      container.value.scrollTop = container.value.scrollHeight
    }
  },
)
</script>

<template>
  <div class="list-wrapper">
    <div ref="container" class="conversation-list" @scroll="onScroll">
      <template v-for="item in items" :key="item.id">
        <UserMessageItem
          v-if="item.type === 'user_message'"
          :item="(item as any)"
        />
        <AssistantMessageItem
          v-else-if="item.type === 'assistant_message'"
          :item="(item as any)"
        />
        <ToolCallItem
          v-else-if="item.type === 'tool_call'"
          :item="(item as any)"
          :status="toolCallInfo[(item as any).tool_call_id]?.status ?? 'pending'"
          :duration="toolCallInfo[(item as any).tool_call_id]?.duration"
        />
        <ToolResultItem
          v-else-if="item.type === 'tool_result'"
          :item="(item as any)"
        />
        <ErrorItem
          v-else-if="item.type === 'error'"
          :item="(item as any)"
        />
      </template>
      <ThinkingItem v-if="loading" />
      <div v-if="items.length === 0 && !loading" class="empty">
        <span class="empty-icon">💬</span>
        <p class="empty-title">Chat Agent</p>
        <p class="empty-sub">Ask anything — I can read and explore files in the demo workspace.</p>
      </div>
    </div>
    <button v-if="showScrollBtn" class="scroll-btn" aria-label="Scroll to bottom" @click="scrollToBottom">↓</button>
  </div>
</template>

<style scoped>
.list-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
}
.list-wrapper::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 340px;
  height: 340px;
  background: url('/logo.png') no-repeat center / contain;
  opacity: 0.25;
  pointer-events: none;
  z-index: 0;
}
.conversation-list {
  height: 100%;
  overflow-y: auto;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
}
.conversation-list > * {
  animation: fadeSlide 0.18s ease-out;
}
@keyframes fadeSlide {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.empty {
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-align: center;
}
.empty-icon { font-size: 2rem; margin-bottom: 4px; }
.empty-title { font-size: 1rem; font-weight: 600; color: #555; margin: 0; }
.empty-sub { font-size: 0.875rem; color: #aaa; margin: 0; max-width: 280px; }
.scroll-btn {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #1a1a1a;
  color: #fff;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
  transition: background 0.15s;
}
.scroll-btn:hover { background: #333; }
</style>
