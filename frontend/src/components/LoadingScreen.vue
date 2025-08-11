<template>
  <div class="loading-overlay">
    <div class="spinner"></div>
    <p>Processing, please wait...</p>
  </div>
</template>

<script setup>
// No script needed for static loading screen
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.spinner {
  border: 8px solid #eee;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 60px; height: 60px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
</style>
