<script setup lang="ts">
import type { ErrorItem } from '../models/conversation'
defineProps<{ item: ErrorItem }>()
</script>

<template>
  <div class="error-item">
    <span class="icon" aria-hidden="true">&#9888;</span>
    <span class="detail">{{ item.detail }}</span>
  </div>
</template>

<style scoped>
.error-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 8px 0;
  padding: 10px 14px;
  background: #fff5f5;
  border-left: 3px solid #e53935;
  border-radius: 0 8px 8px 0;
  color: #c62828;
  font-size: 0.9rem;
  line-height: 1.4;
}
.icon {
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 1px;
}
</style>
