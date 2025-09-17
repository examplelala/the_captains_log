<template>
  <div class="main-header">
    <h1 class="main-title">今日思考空间</h1>
    <p class="main-subtitle">记录想法，明日获得智能建议与人生规划</p>
  </div>
</template>

<style scoped>
.main-header {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  padding: 30px 50px;
  text-align: center;
  position: relative;
}

.main-header::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.5;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.8;
  }
}

.main-title {
  font-size: 3.2em;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff 0%, #667eea 50%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 16px;
  position: relative;
  z-index: 2;
  animation: titleSlide 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes titleSlide {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.main-subtitle {
  font-size: 1.2em;
  color: var(--text-secondary);
  line-height: 1.6;
  position: relative;
  z-index: 2;
  animation: titleSlide 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

@media (max-width: 768px) {
  .main-header {
    padding: 30px 25px;
  }

  .main-title {
    font-size: 2.2em;
  }
}
</style>