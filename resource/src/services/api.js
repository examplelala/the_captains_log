import axios from 'axios'

// API基础配置
const BASE_URL = 'http://localhost:8000'

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

// 思考记录服务
export const thoughtService = {
    async saveThought(thoughtData) {
        return await api.post('/save-thought', thoughtData)
    },

    async getThoughts(date) {
        return await api.get('/thoughts', {
            params: { date }
        })
    }
}

// 建议服务
export const suggestionService = {
    async getDailySuggestions() {
        return await api.get('/suggestions/daily')
    },

    async generateSuggestions(thoughtData) {
        return await api.post('/suggestions/generate', thoughtData)
    }
}

export default api