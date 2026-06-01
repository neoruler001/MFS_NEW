<template>
  <div class="home-view">
    <!-- Animated background layers -->
    <div class="background-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <!-- Main Container -->
    <main class="main-container">
      <!-- Executive Header Section -->
      <header class="executive-header animate-fade-in">
        <div class="header-content">
          <div class="profile-section">
            <div class="avatar-wrapper">
              <div class="avatar-gradient">
                <span>{{ korNm.charAt(0) }}</span>
              </div>
              <div class="avatar-ring"></div>
            </div>
            <div class="user-meta">
              <span class="company-badge">{{ companyNm || 'HD HYUNDAI GROUP' }}</span>
              <h2 class="username-title">
                <span class="user-name">{{ korNm }}</span>
                <span class="greeting-text">님, 환영합니다</span>
              </h2>
            </div>
          </div>
          
          <div class="header-actions">
            <button v-if="isAdmin" @click="navigateTo('admin')" class="glass-btn admin" title="관리 시스템">
              <span class="icon">⚙️</span>
              <span class="label">시스템 관리</span>
            </button>
            <button @click="logout" class="glass-btn logout" title="로그아웃">
              <span class="icon">🚪</span>
              <span class="label">로그아웃</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Balanced Service Grid Section (2 Rows Layout) -->
      <section class="service-section">
        <div class="service-grid">
          <!-- 1. 카드 이용내역 -->
          <div class="service-item animate-stagger-1" @click="navigateTo('card-usage')">
            <div class="card-glass-content">
              <div class="card-top">
                <div class="icon-box primary">💳</div>
                <div class="arrow-circle">→</div>
              </div>
              <div class="card-body">
                <div class="title-group">
                  <h3 class="card-title">법인카드 이용내역</h3>
                  <span class="status-indicator">LIVE</span>
                </div>
                <p class="card-desc">실시간 법인카드 집행 내역과 정산 현황을 스마트하게 모니터링하세요.</p>
              </div>
            </div>
          </div>

          <!-- 2. 예산 관리 -->
          <div class="service-item animate-stagger-2" @click="navigateTo('budget')">
            <div class="card-glass-content">
              <div class="card-top">
                <div class="icon-box secondary">📊</div>
                <div class="arrow-circle">→</div>
              </div>
              <div class="card-body">
                <h3 class="card-title">예산 조회</h3>
                <p class="card-desc">편성 예산과 집행 추이를 실시간 지표로 확인하고 분석합니다.</p>
              </div>
            </div>
          </div>

          <!-- 3. 담당자 연락처 -->
          <div class="service-item animate-stagger-3" @click="navigateTo('contacts')">
            <div class="card-glass-content">
              <div class="card-top">
                <div class="icon-box info">📞</div>
                <div class="arrow-circle">→</div>
              </div>
              <div class="card-body">
                <h3 class="card-title">담당자 연락처</h3>
                <p class="card-desc">시스템 관련 문의 및 업무 지원을 위한 사내 담당자 연락망 정보를 제공합니다.</p>
              </div>
            </div>
          </div>

          <!-- 4. 공지사항 -->
          <div class="service-item animate-stagger-4" @click="navigateTo('notices')">
            <div class="card-glass-content">
              <div class="card-top">
                <div class="icon-box warning">🔔</div>
                <div class="arrow-circle">→</div>
              </div>
              <div class="card-body">
                <h3 class="card-title">주요 공지사항</h3>
                <div class="latest-notice-preview">
                  <p class="notice-text">
                    {{ latestNotice ? latestNotice.SUBJECT : '등록된 공지사항이 없습니다.' }}
                  </p>
                  <span class="notice-date">{{ latestNoticeDate || '2026.05.12' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="system-footer animate-fade-in">
        <div class="footer-line"></div>
        <p>© 2026 HD현대E&T Corporate Card Management System</p>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const notices = ref([])
const latestNotice = computed(() => notices.value[0] || null)

const korNm = ref(localStorage.getItem('kor_nm') || 'Neo')
const companyNm = ref(localStorage.getItem('company_nm') || '')
const isAdmin = ref(localStorage.getItem('is_admin') === 'true')

const latestNoticeDate = computed(() => {
  if (!latestNotice.value || !latestNotice.value.ERDAT) return ''
  const d = latestNotice.value.ERDAT
  if (d.length === 8) {
    return `${d.substr(0, 4)}.${d.substr(4, 2)}.${d.substr(6, 2)}`
  }
  return d
})

const fetchLatestNotice = async () => {
  try {
    const res = await axios.get('/api/v1/notices/notices')
    notices.value = res.data || []
  } catch (err) { console.error(err) }
}

const navigateTo = (routeName) => { router.push({ name: routeName }) }

const logout = () => {
  const wasAdmin = isAdmin.value
  localStorage.clear()
  router.replace(wasAdmin ? '/admin-login' : '/login')
}

onMounted(() => {
  if (!localStorage.getItem('kor_nm')) { logout(); return; }
  fetchLatestNotice()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

.home-view {
  min-height: 100vh;
  background-color: #020617;
  font-family: 'Outfit', sans-serif;
  color: #f8fafc;
  overflow-x: hidden;
  position: relative;
}

/* --- Animated Background --- */
.background-blobs {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  overflow: hidden;
  z-index: 0;
}

.blob {
  position: absolute;
  width: 600px; height: 600px;
  filter: blur(120px);
  opacity: 0.12;
  border-radius: 50%;
  animation: move-blobs 25s infinite alternate;
}

.blob-1 { background: #3b82f6; top: -15%; left: -10%; }
.blob-2 { background: #8b5cf6; bottom: -15%; right: -10%; animation-delay: -5s; }
.blob-3 { background: #06b6d4; top: 35%; left: 35%; animation-delay: -10s; }

@keyframes move-blobs {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(60px, 120px) scale(1.15); }
  100% { transform: translate(-40px, -60px) scale(0.9); }
}

.main-container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 50px 24px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* --- Executive Header --- */
.executive-header {
  margin-bottom: 10px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  padding: 28px 36px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.4);
}

.profile-section { display: flex; align-items: center; gap: 20px; }

.avatar-wrapper { position: relative; }
.avatar-gradient {
  width: 64px; height: 64px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; font-weight: 800; color: white;
}
.avatar-ring {
  position: absolute; top: -5px; left: -5px; right: -5px; bottom: -5px;
  border: 2px solid rgba(59, 130, 246, 0.25);
  border-radius: 25px;
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.15); opacity: 0; }
}

.company-badge {
  font-size: 0.7rem; font-weight: 800; color: #60a5fa;
  letter-spacing: 0.15em; text-transform: uppercase;
  background: rgba(59, 130, 246, 0.1);
  padding: 4px 12px; border-radius: 6px;
  margin-bottom: 8px; display: inline-block;
}

.username-title { font-size: 1.6rem; font-weight: 800; color: #ffffff; margin: 0; }
.greeting-text { font-weight: 400; color: #94a3b8; font-size: 1.1rem; margin-left: 8px; }

.header-actions { display: flex; gap: 12px; }
.glass-btn {
  padding: 14px 24px; border-radius: 16px;
  font-weight: 700; font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; gap: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}
.glass-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: #3b82f6; color: white;
  transform: translateY(-2px);
  box-shadow: 0 12px 24px -8px rgba(59, 130, 246, 0.3);
}

/* --- Service Grid (2 Rows Symmetrical) --- */
.service-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.service-item {
  position: relative;
  border-radius: 32px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  min-height: 240px;
}

.card-glass-content {
  height: 100%;
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(20px);
  padding: 36px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.service-item:hover {
  transform: translateY(-10px);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 40px 80px -15px rgba(0, 0, 0, 0.6);
}

.service-item:hover .card-glass-content {
  background: rgba(30, 41, 59, 0.65);
}

.card-top { display: flex; justify-content: space-between; align-items: flex-start; }

.icon-box {
  width: 64px; height: 64px;
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem;
}
.icon-box.primary { background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.3); }
.icon-box.secondary { background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.3); }
.icon-box.info { background: rgba(6, 182, 212, 0.2); border: 1px solid rgba(6, 182, 212, 0.3); }
.icon-box.warning { background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.3); }

.arrow-circle {
  width: 48px; height: 48px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; color: #64748b; transition: all 0.3s;
}
.service-item:hover .arrow-circle {
  background: #3b82f6; color: white; transform: rotate(-45deg) scale(1.1);
}

.card-body { margin-top: 24px; }
.title-group { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.card-title { font-size: 1.6rem; font-weight: 800; color: white; margin: 0; }
.card-desc { font-size: 1.05rem; color: #94a3b8; line-height: 1.7; font-weight: 500; }

.status-indicator {
  background: rgba(16, 185, 129, 0.15); color: #10b981;
  font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 20px;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.latest-notice-preview {
  margin-top: 10px; padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03); border-radius: 12px;
  display: flex; flex-direction: column; gap: 6px;
}
.notice-text { font-size: 0.95rem; font-weight: 600; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.notice-date { font-size: 0.8rem; color: #64748b; }

/* --- Animations --- */
.animate-fade-in { animation: fadeIn 0.8s ease-out forwards; }
.animate-stagger-1 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.1s both; }
.animate-stagger-2 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.2s both; }
.animate-stagger-3 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.3s both; }
.animate-stagger-4 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.4s both; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

.system-footer { margin-top: 50px; text-align: center; }
.footer-line { height: 1px; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent); margin-bottom: 30px; }
.system-footer p { font-size: 0.85rem; color: #64748b; font-weight: 500; letter-spacing: 0.02em; }

@media (max-width: 900px) {
  .service-grid { grid-template-columns: 1fr; }
  .header-content { flex-direction: column; gap: 24px; align-items: flex-start; padding: 24px; }
  .executive-header { margin-bottom: 0; }
}
</style>
