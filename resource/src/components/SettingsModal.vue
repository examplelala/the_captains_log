<template>
  <div>
    <!-- 遮罩层 -->
    <div
      v-if="visible"
      class="settings-overlay"
      @click="closeModal"
    ></div>
    
    <!-- 设置面板 -->
    <div
      v-if="visible"
      class="settings-panel"
    >
      <div class="panel-header">
        <div class="panel-title">个性化设置</div>
      </div>

      <div class="setting-group">
        <label class="setting-label">城市位置</label>
        <input
          v-model="localConfig.city"
          type="text"
          class="setting-input"
          placeholder="输入城市名称"
        >
      </div>

      <div class="setting-group">
        <label class="setting-label">新闻源</label>
        <select v-model="localConfig.newsSource" class="setting-select">
          <option value="hupu">虎扑</option>
          <option value="weibo">微博</option>
          <option value="zhihu">知乎</option>
          <option value="baidu">百度</option>
        </select>
      </div>

      <div class="setting-group">
        <label class="setting-label">新闻条数</label>
        <select v-model="localConfig.newsLimit" class="setting-select">
          <option :value="3">3条</option>
          <option :value="5">5条</option>
          <option :value="8">8条</option>
        </select>
      </div>

      <div class="button-group">
        <button class="save-btn" @click="applySettings">
          ✅ 应用设置
        </button>
        <button class="close-btn" @click="closeModal">
          ❌
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  config: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'update:config', 'apply-settings'])

const localConfig = ref({
  city: props.config.city,
  newsSource: props.config.newsSource,
  newsLimit: props.config.newsLimit
})

// 监听配置变化
watch(() => props.config, (newConfig) => {
  localConfig.value = { ...newConfig }
}, { deep: true })

// 监听弹窗状态变化
watch(() => props.visible, (visible) => {
  if (visible) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = 'auto'
  }
})

const closeModal = () => {
  emit('update:visible', false)
}

const applySettings = () => {
  const newConfig = {
    city: localConfig.value.city.trim() || '成都银泰城',
    newsSource: localConfig.value.newsSource,
    newsLimit: parseInt(localConfig.value.newsLimit)
  }
  
  emit('update:config', newConfig)
  emit('apply-settings', newConfig)
  closeModal()
}
</script>

<style scoped>
.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  z-index: 999;
}

.settings-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 30px;
  z-index: 1000;
  width: 90%;
  max-width: 400px;
  animation: modalSlide 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modalSlide {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

.panel-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 15px;
  margin-bottom: 25px;
}

.panel-title {
  font-size: 1.4em;
  font-weight: 700;
  color: var(--text-primary);
}

.setting-group {
  margin-bottom: 20px;
}

.setting-label {
  display: block;
  font-size: 0.9em;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-weight: 500;
}

.setting-input,
.setting-select {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--text-primary);
  font-family: inherit;
  transition: all 0.3s ease;
}

.setting-input:focus,
.setting-select:focus {
  outline: none;
  border-color: var(--accent-color);
  background: rgba(255, 255, 255, 0.08);
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 30px;
}

.save-btn {
  flex: 1;
  padding: 12px;
  background: var(--cool-gradient);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(79, 172, 254, 0.3);
}

.close-btn {
  flex: 0 0 auto;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
}
</style>