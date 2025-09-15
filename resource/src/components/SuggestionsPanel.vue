<template>
  <div class="suggestions-panel">
    <div class="panel-header">
      <div class="panel-icon">🎯</div>
      <div class="panel-title">今日建议 & 规划</div>
    </div>
    <div class="suggestions-content">
      <div
        v-for="(suggestion, index) in suggestions"
        :key="index"
        class="suggestion-item"
      >
        <div class="suggestion-category">{{ suggestion.category }}</div>
        <div class="suggestion-text">{{ suggestion.text }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const suggestions = ref([])

const defaultSuggestions = [
  {
    category: "健康建议",
    text: "基于您昨日的思考记录，建议今天安排30分钟户外运动，有助于缓解工作压力并提升创意思维。"
  },
  {
    category: "工作规划",
    text: "您提到的项目进展问题，建议今天上午优先处理核心任务，下午安排团队沟通会议来解决协作难题。"
  },
  {
    category: "学习成长",
    text: "根据您的兴趣方向，推荐今晚阅读相关专业书籍，并做笔记记录关键洞察。"
  },
  {
    category: "生活平衡",
    text: "注意到您最近思考较多工作话题，建议今晚安排一些放松活动，比如听音乐或与朋友聊天。"
  },
  {
    category: "效率提升",
    text: "建议采用番茄工作法来提高专注度，每25分钟休息5分钟，保持高效的工作节奏。"
  },
  {
    category: "人际关系",
    text: "考虑主动联系一位许久未见的朋友，维护重要的人际关系对心理健康很有帮助。"
  }
]

const generateDailySuggestions = () => {
  // 随机选择3-4个建议，模拟AI生成的个性化内容
  const shuffled = [...defaultSuggestions].sort(() => 0.5 - Math.random())
  suggestions.value = shuffled.slice(0, Math.floor(Math.random() * 2) + 3)
}

onMounted(() => {
  generateDailySuggestions()
})

// 暴露刷新方法给父组件
defineExpose({
  generateDailySuggestions
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
}

.suggestions-content {
  line-height: 1.8;
  color: var(--text-secondary);
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 8px;
}

.suggestion-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  position: relative;
  transition: all 0.3s ease;
}

.suggestion-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.suggestion-category {
  font-size: 0.8em;
  color: var(--accent-color);
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.suggestion-text {
  font-size: 0.95em;
  line-height: 1.6;
}

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

@media (max-width: 1200px) {
  .suggestions-panel {
    order: 2;
  }
}

</style>