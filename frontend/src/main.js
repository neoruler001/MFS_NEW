import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

// ✅ Axios 초기 설정
// axios.defaults.baseURL = 'http://localhost:6100' // Vite 프록시 사용을 위해 주석 처리 또는 상대 경로 사용 권장
axios.defaults.baseURL = '' 

const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// ✅ Axios 응답 인터셉터: 세션 만료(401 Unauthorized) 시 로그인 화면으로 자동 이동
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // ✅ 로그인 API 요청(/auth/login)에서 발생하는 401은 세션 만료가 아니므로 리다이렉트 방지
      const isLoginRequest = error.config.url.includes('/auth/login')
      
      if (!isLoginRequest) {
        console.warn('세션이 만료되어 로그인 화면으로 이동합니다.')
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        router.push({ name: 'login' })
      }
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
