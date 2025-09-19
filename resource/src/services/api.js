import axios from 'axios'

// API基础配置
const BASE_URL = 'https://dabinglian.chat/'

const api = axios.create({
    baseURL: BASE_URL,
    timeout: 10000
})

// 响应拦截器
api.interceptors.response.use(
    response => response.data,
    error => {
        console.error('API Error:', error)
        return Promise.reject(error)
    }
)

// 天气服务
export const weatherService = {
    async getWeather(city) {
        const encodedCity = encodeURIComponent(city)
        return await api.get(`/weather/${encodedCity}`)
    }
}

// 新闻服务
export const newsService = {
    async getNews(source, limit = 3) {
        return await api.get(`/news/${source}`, {
            params: { limit }
        })
    }
}


// 创建每日记录

export const createDailyRecord = async (userId, recordData) => {
    try {
        const response = await api.post(`/record/users/${userId}/records/`, recordData)
        return response
    } catch (error) {
        console.error('创建记录失败:', error)
        throw error
    }
}


// 获取今日信息
export const getTodayInfo = async (userId) => {
    try {
        const response = await api.get(`/summary/users/${userId}/today`)
        return response
    } catch (error) {
        console.error('获取今日信息失败:', error)
        throw error
    }
}

// 重新生成AI总结
export const regenerateAISummary = async (userId, recordDate) => {
    try {
        // 对于POST请求，如果没有请求体，可以传递一个空对象作为数据
        const response = await api.post(`/summary/users/${userId}/records/${recordDate}/regenerate-summary`, {})
        return response.data
    } catch (error) {
        console.error('重新生成AI总结失败:', error)
        throw error
    }
}

// 获取用户ID的辅助函数
export const getCurrentUserId = () => {
    return localStorage.getItem('userId') || 1 // 默认用户ID为1
}

export default api