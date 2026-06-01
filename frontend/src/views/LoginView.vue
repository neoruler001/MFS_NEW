<template>
  <div class="login-page">
    <!-- 배경 오로라 애니메이션 요소 -->
    <div class="aurora-bg">
      <div class="blob"></div>
      <div class="blob"></div>
      <div class="blob"></div>
    </div>

    <div class="login-container">
      <div class="login-brand animate-fade-in">
        <h1 class="premium-logo">MFS<span>.</span></h1>
        <p class="brand-subtitle">Corporate Intelligence Platform</p>
      </div>

      <div class="premium-card login-card animate-slide-up">
        <h2 class="card-title">로그인</h2>
        <p class="card-description">시스템 접속을 위해 사번과 비밀번호를 입력하세요.</p>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="input-group">
            <label class="input-label">사번 (Employee ID)</label>
            <div class="input-wrapper">
              <input 
                v-model="username" 
                type="text" 
                placeholder="사번을 입력하세요 (예: A509166)" 
                required
                class="premium-input"
                @input="username = username.toUpperCase()"
              />
              <span class="input-icon">👤</span>
            </div>
          </div>
          
          <div class="input-group">
            <label class="input-label">비밀번호 (Password)</label>
            <div class="input-wrapper">
              <input 
                v-model="password" 
                type="password" 
                placeholder="비밀번호를 입력하세요" 
                required
                class="premium-input"
              />
              <span class="input-icon">🔒</span>
            </div>
          </div>
          
          <button type="submit" :disabled="loading" class="login-submit-btn">
            <span v-if="!loading">로그인 하기</span>
            <span v-else class="loading-dots">접속 중<span>.</span><span>.</span><span>.</span></span>
            <svg v-if="!loading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </button>
        </form>
        
        <transition name="shake">
          <div v-if="error" class="error-container">
            <span class="error-icon">⚠️</span>
            <span>{{ error }}</span>
          </div>
        </transition>
      </div>
      
      <footer class="login-footer animate-fade-in-delayed">
        <p>© 2026 HD Hyundai. All Rights Reserved.</p>
        <div class="footer-links">
          <span>Security</span>
          <span class="dot">·</span>
          <span>Compliance</span>
        </div>
      </footer>
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
const loading = ref(false)
const error = ref('')

// ✅ 이미 로그인된 경우 홈으로 강제 이동
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
    
    // ✅ Neo의 요청: 일반 로그인에서도 client_id(조회 대상 사번)를 전송하여 인증 성공 유도
    params.append('client_id', username.value)
    
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
    
    router.replace('/')
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = '사번 또는 비밀번호가 올바르지 않습니다.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* --- Aurora Background & Animations --- */
.aurora-bg {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #020617;
  overflow: hidden;
  z-index: -1;
}

.blob {
  position: absolute;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
  filter: blur(80px);
  animation: move 20s infinite alternate;
}

.blob:nth-child(2) {
  background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
  animation-duration: 30s;
  animation-delay: -5s;
}

.blob:nth-child(3) {
  background: radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%);
  animation-duration: 25s;
  animation-delay: -10s;
}

@keyframes move {
  from { transform: translate(-10%, -10%); }
  to { transform: translate(20%, 20%); }
}

.animate-fade-in { animation: fadeIn 1s ease-out forwards; }
.animate-fade-in-delayed { animation: fadeIn 1s ease-out 0.5s forwards; opacity: 0; }
.animate-slide-up { animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { 
  from { opacity: 0; transform: translateY(30px); } 
  to { opacity: 1; transform: translateY(0); } 
}

/* --- Login Components --- */
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  font-family: 'Outfit', sans-serif;
}

.login-container {
  width: 100%;
  max-width: 440px;
  padding: 20px;
}

.login-brand {
  text-align: center;
  margin-bottom: 48px;
}

.premium-logo {
  font-size: 4rem;
  font-weight: 900;
  letter-spacing: -0.06em;
  color: #ffffff;
  margin-bottom: 8px;
}

.premium-logo span { color: #3b82f6; }

.brand-subtitle {
  color: #94a3b8;
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.login-card {
  padding: 48px;
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.card-title {
  font-size: 2rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.card-description {
  font-size: 1rem;
  color: #94a3b8;
  margin-bottom: 40px;
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #cbd5e1;
  margin-left: 4px;
}

.input-wrapper {
  position: relative;
}

.premium-input {
  width: 100%;
  padding: 16px 20px 16px 52px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: #ffffff;
  font-size: 1.05rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.premium-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(15, 23, 42, 0.8);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
}

.input-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  opacity: 0.6;
}

.login-submit-btn {
  margin-top: 12px;
  height: 60px;
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  color: #ffffff;
  border: none;
  border-radius: 16px;
  font-weight: 800;
  font-size: 1.15rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
}

.login-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -10px rgba(59, 130, 246, 0.6);
  filter: brightness(1.1);
}

.login-submit-btn:active { transform: translateY(0); }

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}

.error-container {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #f87171;
  font-size: 0.95rem;
  font-weight: 600;
  margin-top: 32px;
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 16px;
}

.shake-enter-active { animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }
@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

.login-footer {
  margin-top: 48px;
  text-align: center;
}

.login-footer p {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 8px;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
}
</style>
