<script setup lang="ts">
import type { ToolResult } from '../models/conversation'
defineProps<{ item: ToolResult }>()
</script>

<template>
  <div class="tool-result">
    <div v-if="item.truncated" class="truncated-badge">truncated</div>
    <!-- plain text only — never v-html -->
    <pre class="content">{{ item.content }}</pre>
  </div>
</template>

<style scoped>
.tool-result {
  margin: 4px 0 8px;
  border-left: 3px solid #ffd900;
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
}
.truncated-badge {
  display: inline-block;
  margin: 6px 14px 0;
  padding: 1px 8px;
  background: #ffd900;
  color: #1a1a1a;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
