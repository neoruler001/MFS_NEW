<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo-section">
        <h1 class="premium-title">MFS</h1>
        <p class="subtitle">Mobile Finance System</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <input 
            v-model="username" 
            type="text" 
            placeholder="접속 사번 (아이디)" 
            required
            class="premium-input"
            @input="username = username.toUpperCase()"
          />
        </div>
        <div class="input-group">
          <input 
            v-model="password" 
            type="password" 
            placeholder="비밀번호" 
            required
            class="premium-input"
          />
        </div>
        <!-- 사용자 요청: 로그인할 때 사번, 비밀번호 아래 사용자 사번이라고 항목을 추가 -->
        <div class="input-group">
          <input 
            v-model="targetPernr" 
            type="text" 
            placeholder="조회할 대상 사용자 사번 (선택)" 
            class="premium-input target-input"
            @input="targetPernr = targetPernr.toUpperCase()"
          />
        </div>
        
        <button type="submit" :disabled="loading" class="premium-button">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
      
      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const password = ref('')
const targetPernr = ref('')  // 새로 추가된 대리 사번 입력 변수
const loading = ref(false)
const error = ref('')

// ✅ 이미 로그인된 경우 홈으로 강제 이동 (브라우저 뒤로가기 대응)
onMounted(() => {
  if (localStorage.getItem('token')) {
    router.replace('/')
  }
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const params = new URLSearchParams()
    params.append('username', username.value)
    params.append('password', password.value)
    // FastAPI OAuth2PasswordRequestForm 사양에서 추가 데이터를 받기 쉬운 client_id 재활용
    if (targetPernr.value) {
      params.append('client_id', targetPernr.value)
    }
    
    const res = await axios.post('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('kor_nm', res.data.kor_nm || '')
    localStorage.setItem('company_nm', res.data.company_nm || '')
    localStorage.setItem('is_admin', res.data.is_admin ? 'true' : 'false')
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
    
    // ✅ router.push 대신 replace를 사용하여 히스토리 스택 관리
    router.replace('/')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail
    } else if (err.response && err.response.status === 401) {
      error.value = '사번 또는 비밀번호가 올바르지 않습니다.'
    } else {
      error.value = '서버와의 통신에 실패했습니다.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--bg-main);
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: var(--space-xl);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.logo-section {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.premium-title {
  font-family: 'Outfit', sans-serif;
  font-size: 3.5rem;
  font-weight: 800;
  margin: 0;
  color: #ffffff;
  letter-spacing: -0.05em;
}

.subtitle {
  color: var(--color-secondary);
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 4px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.input-group {
  display: flex;
  flex-direction: column;
}

.premium-input {
  width: 100%;
  padding: 1rem;
  background: var(--bg-main);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.premium-input:focus {
  outline: none;
  border-color: var(--color-secondary);
  background: #1e293b;
}

.premium-input::placeholder {
  color: var(--text-muted);
}

.target-input {
  border-style: dashed;
  border-color: var(--color-secondary-soft);
}

.premium-button {
  width: 100%;
  padding: 1rem;
  background: var(--color-secondary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-md);
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: var(--space-sm);
}

.premium-button:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.premium-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-msg {
  color: var(--color-danger);
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-md);
}
</style>
