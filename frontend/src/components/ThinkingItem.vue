<template>
  <div class="thinking">
    <span class="dot" /><span class="dot" /><span class="dot" />
  </div>
</template>

<style scoped>
.thinking {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 16px;
  margin: 4px 0;
}
.dot {
  width: 8px;
  height: 8px;
  background: #e08000;
  border-radius: 50%;
  animation: bounce 1.2s ease-in-out infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-6px); opacity: 1; }
}
</style>
