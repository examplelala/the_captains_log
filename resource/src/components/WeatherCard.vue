<template>
  <div class="weather-section">
    <div class="weather-card" @click="refreshWeather">
      <div class="weather-icon">{{ weatherData.icon }}</div>
      <div class="temperature">{{ weatherData.temperature }}</div>
      <div class="weather-desc">{{ weatherData.description }}</div>
      <div class="weather-location">{{ city }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, inject } from 'vue'
import { weatherService } from '../services/api'

const props = defineProps({
  city: {
    type: String,
    default: '成都银泰城'
  }
})

const showToast = inject('showToast')

const weatherData = ref({
  icon: '🌤️',
  temperature: '加载中...',
  description: '正在获取天气信息',
  location: props.city
})

const loadWeather = async () => {
  try {
    const data = await weatherService.getWeather(props.city)
    const weather = data.current_weather
    const weatherInfo = getWeatherInfo(weather.weathercode)
    
    weatherData.value = {
      icon: weatherInfo.icon,
      temperature: `${weather.temperature}°C`,
      description: weatherInfo.desc,
      location: props.city
    }
  } catch (error) {
    console.error('Weather loading error:', error)
    weatherData.value = {
      icon: '❌',
      temperature: '天气服务',
      description: '暂时无法连接',
      location: props.city
    }
  }
}

const getWeatherInfo = (code) => {
  const weatherCodes = {
    0: { desc: '晴朗', icon: '☀️' },
    1: { desc: '大部分晴朗', icon: '🌤️' },
    2: { desc: '部分多云', icon: '⛅' },
    3: { desc: '阴天', icon: '☁️' },
    45: { desc: '雾', icon: '🌫️' },
    48: { desc: '结霜雾', icon: '🌫️' },
    51: { desc: '小雨', icon: '🌦️' },
    53: { desc: '中雨', icon: '🌧️' },
    55: { desc: '大雨', icon: '🌧️' },
    61: { desc: '小雨', icon: '🌦️' },
    63: { desc: '中雨', icon: '🌧️' },
    65: { desc: '大雨', icon: '⛈️' },
    80: { desc: '阵雨', icon: '🌦️' },
    81: { desc: '中等阵雨', icon: '🌧️' },
    82: { desc: '强阵雨', icon: '⛈️' },
    95: { desc: '雷暴', icon: '⛈️' }
  }
  return weatherCodes[code] || { desc: '未知', icon: '❓' }
}

const refreshWeather = () => {
  loadWeather()
  if (showToast) {
    showToast('正在刷新天气信息...')
  }
}

// 监听城市变化
watch(() => props.city, () => {
  loadWeather()
})

onMounted(() => {
  loadWeather()
})
</script>

<style scoped>
.weather-section {
  padding: 30px;
  position: relative;
}

.weather-card {
  background: linear-gradient(135deg, rgba(255, 154, 86, 0.15) 0%, rgba(255, 173, 86, 0.05) 100%);
  border: 1px solid rgba(255, 154, 86, 0.2);
  border-radius: 24px;
  padding: 25px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.weather-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: conic-gradient(from 0deg, transparent, rgba(255, 154, 86, 0.1), transparent);
  animation: weatherRotate 8s linear infinite;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.weather-card:hover::before {
  opacity: 1;
}

.weather-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(255, 154, 86, 0.2);
}

@keyframes weatherRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.weather-icon {
  font-size: 3.5em;
  margin-bottom: 15px;
  display: block;
  animation: weatherFloat 3s ease-in-out infinite;
}

@keyframes weatherFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

.temperature {
  font-size: 2.5em;
  font-weight: 800;
  margin-bottom: 8px;
  background: var(--warm-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.weather-desc {
  color: var(--text-secondary);
  font-size: 0.95em;
  margin-bottom: 15px;
}

.weather-location {
  font-size: 0.8em;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
}
</style>