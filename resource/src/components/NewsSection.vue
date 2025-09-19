<template>
  <div class="news-section">
    <div class="section-title">
      <div class="section-icon">📰</div>
      <span>{{ newsSourceNames[source] }}热点</span>
    </div>
    <div class="news-list">
      <div 
        v-if="loading" 
        class="loading"
      >
        正在加载新闻...
      </div>
      <div 
        v-else-if="error" 
        class="error"
      >
        📰 新闻加载失败<br>
        <small>请检查网络连接</small>
      </div>
      <div 
        v-else-if="newsList.length === 0" 
        class="empty"
      >
        📭 暂无新闻数据
      </div>
      <div
        v-else
        v-for="item in newsList"
        :key="item.id || item.title"
        class="news-item"
        @click="openNews(item.url)"
      >
        <div class="news-title">{{ item.title }}</div>
        <div class="news-meta">
          <span>{{ formatTime(item.publish_time) }}</span>
          <span class="news-source">{{ item.source?.toUpperCase() || source.toUpperCase() }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { newsService } from '../services/api'

const props = defineProps({
  source: {
    type: String,
    default: 'hupu'
  },
  limit: {
    type: Number,
    default: 3
  }
})

const newsSourceNames = {
  "baidu": "百度",
  "shaoshupai": "少数派",
  "weibo": "微博",
  "zhihu": "知乎",
  "36kr": "36氪",
  "52pojie": "吾爱破解",
  "bilibili": "哔哩哔哩",
  "douban": "豆瓣",
  "hupu": "虎扑",
  "tieba": "贴吧",
  "juejin": "掘金",
  "douyin": "抖音",
  "v2ex": "V2EX",
  "jinritoutiao": "今日头条",
  "stackoverflow": "Stack Overflow",
  "github": "GitHub",
  "hackernews": "Hacker News"
};


const newsList = ref([])
const loading = ref(false)
const error = ref(false)

const loadNews = async () => {
  loading.value = true
  error.value = false
  
  try {
    const data = await newsService.getNews(props.source, props.limit)
    newsList.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('News loading error:', err)
    error.value = true
    newsList.value = []
  } finally {
    loading.value = false
  }
}

const formatTime = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const openNews = (url) => {
  if (url) {
    window.open(url, '_blank')
  }
}

// 监听属性变化
watch([() => props.source, () => props.limit], () => {
  loadNews()
})

onMounted(() => {
  loadNews()
})
</script>

<style scoped>
.news-section {
  flex: 1;
  padding: 30px;
  overflow: hidden;
}

.section-title {
  font-size: 1.2em;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  width: 24px;
  height: 24px;
  background: var(--cool-gradient);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.loading,
.empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  padding: 20px;
}

.error {
  text-align: center;
  color: #ff6b6b;
  padding: 20px;
}

.error small {
  opacity: 0.7;
}

.news-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.news-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  transition: left 0.6s ease;
}

.news-item:hover::before {
  left: 100%;
}

.news-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateX(4px);
}

.news-title {
  font-size: 0.9em;
  line-height: 1.4;
  margin-bottom: 8px;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  font-size: 0.75em;
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-source {
  background: rgba(0, 212, 255, 0.2);
  color: var(--accent-color);
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.7em;
  font-weight: 500;
}

.news-list::-webkit-scrollbar {
  width: 6px;
}

.news-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.news-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.news-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .news-section {
    flex: 0 0 250px;
    padding: 15px;
  }
}
</style>