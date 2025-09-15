<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo">✨ LifeSync</div>
      <div class="tagline">智能生活规划助手</div>
    </div>

    <WeatherCard :city="config.city" />

    <NewsSection 
      :source="config.newsSource"
      :limit="config.newsLimit"
    />

    <button class="settings-toggle" @click="$emit('settings-toggle')">
      ⚙️ 个性化设置
    </button>
  </div>
</template>

<script setup>
import WeatherCard from './WeatherCard.vue'
import NewsSection from './NewsSection.vue'

defineProps({
  config: {
    type: Object,
    required: true
  }
})

defineEmits(['settings-toggle'])
</script>

<style scoped>
.sidebar {
  grid-area: sidebar;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
  pointer-events: none;
}

.sidebar-header {
  padding: 40px 30px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  z-index: 2;
}

.logo {
  font-size: 1.8em;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
  animation: logoGlow 3s ease-in-out infinite alternate;
}

@keyframes logoGlow {
  0% {
    filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.3));
  }
  100% {
    filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.6));
  }
}

.tagline {
  font-size: 0.9em;
  color: var(--text-secondary);
  line-height: 1.6;
}

.settings-toggle {
  margin: 0 30px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  padding: 12px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.85em;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .sidebar {
    border-right: none;
    border-top: 1px solid var(--glass-border);
    flex-direction: row;
    overflow-x: auto;
    padding: 20px;
  }
}
</style>