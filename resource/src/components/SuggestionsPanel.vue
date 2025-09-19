<template>
  <div class="suggestions-panel">
    <div class="panel-header">
      <div class="panel-icon">🎯</div>
      <div class="panel-title">今日建议 & 规划</div>
      <div class="panel-status">{{ statusText }}</div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载今日总结...</p>
    </div>

    <!-- 有AI总结时显示 -->
    <div v-else-if="todayInfo.has_summary" class="suggestions-content">
      <!-- 成就总结 -->
      <div v-if="todayInfo.ai_summary.achievements_summary" class="summary-section">
        <div class="section-header">🏆 今日成就</div>
        <div class="summary-text">{{ todayInfo.ai_summary.achievements_summary }}</div>
      </div>
    <!--生产力分析-->>
      <div v-if="todayInfo.ai_summary.productivity_analysis" class="summary-section">
        <div class="section-header">🚀 生产力分析</div>
        <div class="summary-text">{{ todayInfo.ai_summary.productivity_analysis }}</div>
      </div>
    <!--情绪分析-->>
      <div v-if="todayInfo.ai_summary.mood_analysis" class="summary-section">
        <div class="section-header">😊 情绪分析</div>
        <div class="summary-text">{{ todayInfo.ai_summary.mood_analysis }}</div>
      </div>
      <!-- 明日建议 -->
      <div v-if="todayInfo.ai_summary.tomorrow_suggestions.length > 0" class="section">
        <div class="section-header">💡 明日建议</div>
        <div
          v-for="(suggestion, index) in todayInfo.ai_summary.tomorrow_suggestions"
          :key="'suggestion-' + index"
          class="suggestion-item"
        >
          <div class="suggestion-category">建议 {{ index + 1 }}</div>
          <div class="suggestion-text">{{ suggestion }}</div>
        </div>
      </div>

      <!-- 优先任务 -->
      <div v-if="todayInfo.ai_summary.priority_tasks.length > 0" class="section">
        <div class="section-header">⚡ 优先任务</div>
        <div
          v-for="(task, index) in todayInfo.ai_summary.priority_tasks"
          :key="'task-' + index"
          class="suggestion-item priority-task"
        >
          <div class="suggestion-category">优先级 {{ index + 1 }}</div>
          <div class="suggestion-text">{{ task }}</div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <button @click="refreshSummary" class="refresh-btn" :disabled="refreshing">
          {{ refreshing ? '🔄 刷新中...' : '🔄 刷新' }}
        </button>
        <button @click="regenerateSummary" class="regenerate-btn" :disabled="regenerating">
          {{ regenerating ? '⏳ 重新生成中...' : '✨ 重新生成' }}
        </button>
      </div>

      <!-- 生成时间 -->
      <div class="meta-info">
        <small>生成时间: {{ formatTime(todayInfo.ai_summary.created_at) }}</small>
      </div>
    </div>

    <!-- 没有总结时的状态 -->
    <div v-else class="no-summary-state">
      <div class="empty-icon">📝</div>
      <div class="empty-title">还没有今日总结</div>
      <div class="empty-desc">完成今日的思考记录后，AI将为您生成个性化的建议和规划</div>
      <button @click="refreshSummary" class="check-btn">
        检查是否有新总结
      </button>
    </div>

    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <div class="error-icon">❌</div>
      <div class="error-message">{{ error }}</div>
      <button @click="loadTodayInfo" class="retry-btn">重试</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject,computed } from 'vue'
import { getTodayInfo, regenerateAISummary,getCurrentUserId } from '../services/api' // 根据你的路径调整

const showToast = inject('showToast')

// 响应式数据
const todayInfo = ref({
  date: '',
  ai_summary: null,
  has_summary: false
})
const loading = ref(true)
const refreshing = ref(false)
const regenerating = ref(false)
const error = ref('')

// 计算属性
const statusText = computed(() => {
  if (loading.value) return '加载中...'
  if (error.value) return '加载失败'
  if (todayInfo.value.has_summary) return `${todayInfo.value.date} 的智能分析`
  return '等待记录生成总结'
})


// 加载今日信息
const loadTodayInfo = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const userId = getCurrentUserId()
    const data = await getTodayInfo(userId)
    console.log(data)
    todayInfo.value = data
    
    if (data.has_summary) {
      showToast('今日AI总结已加载 ✨')
    }
  } catch (err) {
    console.error('加载今日信息失败:', err)
    error.value = '加载失败，请稍后重试'
    showToast('加载今日信息失败 ❌')
  } finally {
    loading.value = false
  }
}

// 刷新总结
const refreshSummary = async () => {
  if (refreshing.value) return
  
  refreshing.value = true
  try {
    const userId = getCurrentUserId()
    const data = await getTodayInfo(userId)
    todayInfo.value = data
    showToast('总结已刷新 ✅')
  } catch (err) {
    console.error('刷新失败:', err)
    showToast('刷新失败，请稍后重试 ❌')
  } finally {
    refreshing.value = false
  }
}

// 重新生成总结
const regenerateSummary = async () => {
  if (regenerating.value) return
  
  regenerating.value = true
  try {
    const userId = getCurrentUserId()
    await regenerateAISummary(userId, todayInfo.value.date)
    showToast('AI正在重新生成总结，请稍后刷新 ⏳')
    
    // 延迟刷新，给AI生成时间
    setTimeout(async () => {
      await refreshSummary()
      regenerating.value = false
    }, 10000) // 10秒后自动刷新
    
  } catch (err) {
    console.error('重新生成失败:', err)
    showToast('重新生成失败，请稍后重试 ❌')
    regenerating.value = false
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '未知'
  return new Date(timestamp).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 暴露方法给父组件
defineExpose({
  refreshSummary,
  loadTodayInfo
})

// 组件挂载时加载数据
onMounted(() => {
  loadTodayInfo()
})
</script>

<style scoped>
.suggestions-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 32px;
  padding: 40px;
  position: relative;
  overflow: hidden;
  animation: panelSlide 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.4s both;
}

@keyframes panelSlide {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.suggestions-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
  animation: borderGlow 3s ease-in-out infinite;
}

@keyframes borderGlow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-icon {
  width: 48px;
  height: 48px;
  background: var(--cool-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5em;
  animation: iconFloat 3s ease-in-out infinite;
}

@keyframes iconFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-4px) rotate(5deg);
  }
}

.panel-title {
  font-size: 1.4em;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
}

.panel-status {
  font-size: 0.8em;
  color: var(--text-secondary);
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 内容区域 */
.suggestions-content {
  line-height: 1.8;
  color: var(--text-secondary);
  max-height: 50vh;
  overflow-y: auto;
  padding-right: 8px;
}

.section {
  margin-bottom: 24px;
}

.section-header {
  font-size: 1em;
  font-weight: 600;
  color: var(--accent-color);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.summary-section {
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.summary-text {
  font-size: 0.95em;
  line-height: 1.6;
  color: var(--text-primary);
}

.suggestion-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 12px;
  position: relative;
  transition: all 0.3s ease;
}

.suggestion-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-1px);
}

.priority-task {
  border-left: 3px solid var(--accent-color);
}

.suggestion-category {
  font-size: 0.75em;
  color: var(--accent-color);
  font-weight: 600;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.suggestion-text {
  font-size: 0.9em;
  line-height: 1.5;
}

/* 操作按钮 */
.actions {
  display: flex;
  gap: 12px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.refresh-btn, .regenerate-btn, .check-btn, .retry-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.regenerate-btn {
  background: var(--cool-gradient);
  color: white;
}

.regenerate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(79, 172, 254, 0.3);
}

.refresh-btn:disabled, .regenerate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 空状态 */
.no-summary-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 3em;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 1.1em;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 0.9em;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 24px;
}

.check-btn {
  background: var(--cool-gradient);
  color: white;
}

.check-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(79, 172, 254, 0.3);
}

/* 错误状态 */
.error-state {
  text-align: center;
  padding: 20px;
}

.error-icon {
  font-size: 2em;
  margin-bottom: 12px;
}

.error-message {
  color: #ff6b6b;
  margin-bottom: 16px;
}

.retry-btn {
  background: #ff6b6b;
  color: white;
}

.retry-btn:hover {
  background: #ff5252;
}

/* 元信息 */
.meta-info {
  text-align: right;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.meta-info small {
  color: var(--text-secondary);
  font-size: 0.75em;
}

/* 滚动条样式 */
.suggestions-content::-webkit-scrollbar {
  width: 6px;
}

.suggestions-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.suggestions-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.suggestions-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .suggestions-panel {
    order: 2;
  }
}

@media (max-width: 768px) {
  .suggestions-panel {
    padding: 24px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .refresh-btn, .regenerate-btn {
    width: 100%;
  }
}
</style>