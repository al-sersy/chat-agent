<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ToolResult } from '../models/conversation'

const props = defineProps<{ item: ToolResult }>()

const expanded = ref(false)
const isLong = computed(() => props.item.content.split('\n').length > 9 || props.item.content.length > 500)
</script>

<template>
  <div class="tool-result">
    <div v-if="item.truncated" class="truncated-badge">truncated</div>
    <!-- plain text only — never v-html -->
    <pre class="content" :class="{ collapsed: !expanded && isLong }">{{ item.content }}</pre>
    <button v-if="isLong" class="toggle-btn" @click="expanded = !expanded">
      {{ expanded ? 'Collapse ↑' : 'Show full output ↓' }}
    </button>
  </div>
</template>

<style scoped>
.tool-result {
  margin: 4px 0 8px;
  border-left: 3px solid #e08000;
  background: #fafafa;
  border-radius: 0 8px 8px 0;
  overflow: hidden;
}
.content {
  padding: 10px 14px;
  font-size: 0.8rem;
  font-family: ui-monospace, monospace;
  white-space: pre-wrap;
  word-break: break-all;
  color: #333;
  margin: 0;
  transition: max-height 0.2s ease;
}
.content.collapsed {
  max-height: 180px;
  overflow: hidden;
  -webkit-mask-image: linear-gradient(to bottom, black 55%, transparent 100%);
  mask-image: linear-gradient(to bottom, black 55%, transparent 100%);
}
.toggle-btn {
  display: block;
  width: 100%;
  padding: 6px;
  background: none;
  border: none;
  border-top: 1px solid #eee;
  font-size: 0.75rem;
  color: #999;
  cursor: pointer;
  font-family: inherit;
  text-align: center;
  transition: color 0.15s, background 0.15s;
}
.toggle-btn:hover { color: #555; background: rgba(0,0,0,0.03); }
.truncated-badge {
  display: inline-block;
  margin: 6px 14px 0;
  padding: 1px 8px;
  background: #e08000;
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
