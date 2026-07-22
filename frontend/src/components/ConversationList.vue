<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ConversationItem } from '../models/conversation'
import UserMessageItem from './UserMessageItem.vue'
import AssistantMessageItem from './AssistantMessageItem.vue'
import ToolCallItem from './ToolCallItem.vue'
import ToolResultItem from './ToolResultItem.vue'
import ErrorItem from './ErrorItem.vue'

const props = defineProps<{ items: ConversationItem[] }>()

const container = ref<HTMLElement | null>(null)

watch(
  () => props.items.length,
  async () => {
    await nextTick()
    if (container.value) {
      container.value.scrollTop = container.value.scrollHeight
    }
  },
)
</script>

<template>
  <div ref="container" class="conversation-list">
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
    <div v-if="items.length === 0" class="empty">
      Ask anything — the AI can read and explore files in the demo workspace.
    </div>
  </div>
</template>

<style scoped>
.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
}
.empty {
  margin: auto;
  color: #aaa;
  font-size: 0.95rem;
  text-align: center;
}
</style>
