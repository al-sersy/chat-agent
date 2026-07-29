<script setup lang="ts">
import type { ToolCall } from '../models/conversation'
defineProps<{ item: ToolCall; status: 'pending' | 'success' | 'error'; duration?: string }>()
</script>

<template>
  <div class="tool-call">
    <div class="tool-header">
      <span v-if="status === 'pending'" class="spinner" aria-hidden="true" />
      <span v-else-if="status === 'success'" class="icon success" aria-label="success">✓<span v-if="duration" class="duration"> {{ duration }}</span></span>
      <span v-else class="icon error" aria-label="error">✗</span>
      <span class="label">Tool call: <strong>{{ item.tool_name }}</strong></span>
    </div>
    <details v-if="Object.keys(item.arguments).length" class="args">
      <summary class="args-summary">Arguments</summary>
      <pre class="args-pre">{{ JSON.stringify(item.arguments, null, 2) }}</pre>
    </details>
  </div>
</template>

<style scoped>
.tool-call {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 6px 0;
  padding: 8px 14px;
  background: #fff3e0;
  border: 1px dashed #e08000;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #555;
}
.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.label strong {
  color: #1a1a1a;
}
.args { margin-top: 2px; }
.args-summary {
  cursor: pointer;
  font-size: 0.78rem;
  color: #999;
  user-select: none;
}
.args-summary:hover { color: #555; }
.args-pre {
  margin: 4px 0 0;
  font-size: 0.75rem;
  font-family: ui-monospace, monospace;
  white-space: pre-wrap;
  word-break: break-all;
  color: #444;
  background: rgba(0,0,0,0.04);
  border-radius: 4px;
  padding: 6px 8px;
}
.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #e08000;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}
.icon {
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
  line-height: 1;
}
.icon.success { color: #2e7d32; }
.icon.error   { color: #c62828; }
.duration { font-size: 0.75rem; font-weight: 400; color: #888; }
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
