<script setup lang="ts">
import type { ToolCall } from '../models/conversation'
defineProps<{ item: ToolCall }>()
</script>

<template>
  <div class="tool-call">
    <span class="spinner" aria-hidden="true" />
    <span class="label">Tool call: <strong>{{ item.tool_name }}</strong></span>
  </div>
</template>

<style scoped>
.tool-call {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 6px 0;
  padding: 8px 14px;
  background: #fffde7;
  border: 1px dashed #ffd900;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #555;
}
.label strong {
  color: #1a1a1a;
}
.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #ffd900;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
