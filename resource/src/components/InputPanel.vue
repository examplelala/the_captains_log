<template>
  <div class="input-area">
    <div class="input-panel">
      <div class="input-header">
        <div class="input-title">今日思考记录</div>
        <div class="input-subtitle">写下你的想法、困惑、目标或感悟</div>
      </div>
      <textarea
        v-model="thoughtContent"
        class="thought-input"
        placeholder="今天有什么想法想要记录？

• 工作中遇到的挑战和思考
• 对未来的规划和目标  
• 生活中的感悟和体会
• 想要改变或改进的地方
• 学到的新知识或技能

这些内容将在明天为您生成个性化的建议和规划..."
        @input="handleInput"
      ></textarea>
      <div class="input-actions">
        <div class="save-status">{{ saveStatus }}</div>
        <button class="save-btn" @click="saveThought">
          💾 保存今日思考
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { createDailyRecord, getCurrentUserId } from '../services/api'
const showToast = inject('showToast')

const thoughtContent = ref('')
const saveStatus = ref('等待输入...')
let autoSaveTimer = null
let lastSavedContent = ''

const handleInput = () => {
  clearTimeout(autoSaveTimer)
  saveStatus.value = '输入中...'

  autoSaveTimer = setTimeout(() => {
    const content = thoughtContent.value.trim()
    if (content && content !== lastSavedContent) {
      saveStatus.value = '自动保存中...'
      setTimeout(() => {
        saveStatus.value = '已自动保存 💾'
        lastSavedContent = content
      }, 500)
    } else {
      saveStatus.value = '等待输入...'
    }
  }, 2000)
}

const saveThought = async () => {
  const content = thoughtContent.value.trim()

  if (!content) {
    showToast('请输入一些内容再保存 📝')
    return
  }

  try {
    // 模拟保存数据
    const recordData  = {
      content: content,
      mood_score: 0,
      work_activities: [],
      personal_activities: [],
      learning_activities: [],
      health_activities: [],
      goals_achieved: [],
      challenges_faced: [],
      reflections: "string"
    }

    const userId = getCurrentUserId()
    const response = await createDailyRecord(userId, recordData)

    lastSavedContent = content
    saveStatus.value = '已保存 ✅'
    showToast('今日思考已保存，明天将为您生成个性化建议 🎯')


  } catch (error) {
    console.error('Save error:', error)
    saveStatus.value = '保存失败 ❌'
    showToast('保存失败，请稍后重试 ❌')
  }
}

onMounted(() => {
  // 加载已保存的内容（可选）
  // loadSavedThought()
})
</script>

<style scoped>
.input-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: panelSlide 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.6s both;
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

.input-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 32px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  flex: 1;
}

.input-header {
  margin-bottom: 25px;
}

.input-title {
  font-size: 1.4em;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.input-subtitle {
  font-size: 0.9em;
  color: var(--text-secondary);
}

.thought-input {
  width: 100%;
  min-height: 400px;
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 25px;
  font-family: inherit;
  font-size: 1em;
  line-height: 1.6;
  color: var(--text-primary);
  resize: vertical;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}

.thought-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.thought-input:focus {
  outline: none;
  border-color: var(--accent-color);
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 0 0 4px rgba(0, 212, 255, 0.1);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.save-status {
  font-size: 0.85em;
  color: var(--text-secondary);
}

.save-btn {
  background: var(--cool-gradient);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 16px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.save-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s ease;
}

.save-btn:hover::before {
  left: 100%;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(79, 172, 254, 0.3);
}
</style>