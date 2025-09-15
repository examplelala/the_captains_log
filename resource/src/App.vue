<template>
  <div class="app-container">
    <!-- 左侧栏 -->
    <Sidebar 
      :config="config"
      @settings-toggle="handleSettingsToggle"
    />

    <!-- 主内容区域 -->
    <div class="main-content">
      <MainHeader />
      
      <div class="content-area">
        <!-- 左侧：今日建议 -->
        <SuggestionsPanel />

        <!-- 右侧：思考输入 -->
        <InputPanel />
      </div>
    </div>

    <!-- 设置面板 -->
    <SettingsModal 
      v-model:visible="showSettings"
      v-model:config="config"
      @apply-settings="handleApplySettings"
    />

    <!-- 全局提示 -->
    <Toast 
      v-if="toast.show"
      :message="toast.message"
      @close="hideToast"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import Sidebar from './components/Sidebar.vue'
import MainHeader from './components/MainHeader.vue'
import SuggestionsPanel from './components/SuggestionsPanel.vue'
import InputPanel from './components/InputPanel.vue'
import SettingsModal from './components/SettingsModal.vue'
import Toast from './components/Toast.vue'

// 响应式数据
const config = ref({
  city: '成都银泰城',
  newsSource: 'hupu',
  newsLimit: 3
})

const showSettings = ref(false)

const toast = ref({
  show: false,
  message: ''
})

// 方法
const handleSettingsToggle = () => {
  showSettings.value = true
}

const handleApplySettings = (newConfig) => {
  config.value = { ...newConfig }
  showToast('设置已应用 ✅')
}

const showToast = (message) => {
  toast.value = {
    show: true,
    message
  }
}

const hideToast = () => {
  toast.value.show = false
}

// 向子组件提供全局方法
provide('showToast', showToast)
provide('config', config)

// 生命周期
onMounted(() => {
  console.log('LifeSync Dashboard Ready ✨')
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: grid;
  grid-template-areas: "sidebar main-content";
  grid-template-columns: 360px 1fr;
  gap: 0;
}

.main-content {
  grid-area: main-content;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.content-area {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
  padding: 50px;
  min-height: 0;
}

@media (max-width: 1200px) {
  .app-container {
    grid-template-columns: 300px 1fr;
  }

  .content-area {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .app-container {
    grid-template-columns: 1fr;
    grid-template-areas: "main-content" "sidebar";
    grid-template-rows: 1fr auto;
  }

  .content-area {
    padding: 25px;
  }
}
</style>