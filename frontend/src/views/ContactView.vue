<template>
  <div class="contact-view">
    <div class="fixed-top-area">
      <header class="view-header">
        <div class="header-left">
          <button @click="router.push('/')" class="nav-icon-btn home" title="홈으로">
            <span class="icon">🏠</span>
          </button>
          <div class="title-group">
            <p class="view-badge">EMERGENCY CONTACTS</p>
            <h2 class="view-title">담당자 연락처</h2>
          </div>
        </div>
        <div class="header-right">
          <button class="glass-btn refresh" @click="fetchContacts" :class="{ spinning: loading }">
            <span class="icon">↻</span>
            <span class="label">새로고침</span>
          </button>
          <button @click="router.back()" class="glass-btn back" title="뒤로가기">
            <span class="icon">←</span>
            <span class="label">뒤로가기</span>
          </button>
        </div>
      </header>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="modern-loader"></div>
      <p>연락처 데이터를 불러오는 중입니다...</p>
    </div>
    
    <div v-else class="contact-grid">
      <div v-for="(item, idx) in contacts" :key="idx" class="contact-card">
        <div class="card-content">
          <div class="header-row">
            <div class="avatar-box">
              {{ item.NAME ? item.NAME[0] : '?' }}
            </div>
            <div class="user-info">
              <div class="name-row">
                <span class="user-name">{{ item.NAME }}</span>
                <span class="user-title">{{ item.TITLE }}</span>
              </div>
              <div class="user-dept">{{ item.DIVISION }}</div>
              <div class="phone-row">
                <svg class="phone-icon" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M6.62,10.79C8.06,13.62 10.38,15.94 13.21,17.38L15.41,15.18C15.69,14.9 16.08,14.82 16.43,14.93C17.55,15.3 18.75,15.5 20,15.5A1,1 0 0,1 21,16.5V20A1,1 0 0,1 20,21A17,17 0 0,1 3,4A1,1 0 0,1 4,3H7.5A1,1 0 0,1 8.5,4C8.5,5.25 8.7,6.45 9.07,7.57C9.18,7.92 9.1,8.31 8.82,8.59L6.62,10.79Z" />
                </svg>
                <a :href="'tel:' + item.TEL" class="phone-number">{{ item.TEL }}</a>
              </div>
              
              <!-- 업무 구분 태그 (이미지 스타일 복구) -->
              <div class="task-badge-row">
                <span class="task-badge">({{ item.REMARK || '업무' }})</span>
              </div>
            </div>
          </div>
          
          <div class="divider"></div>
          
          <div class="description-row">
            <p class="task-description">{{ item.TASK || '재무시스템 개발 및 유지보수 수행' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const contacts = ref([])
const loading = ref(true)

const fetchContacts = async () => {
  try {
    const res = await axios.get('/api/v1/contacts/list')
    contacts.value = res.data || []
  } catch (err) { 
    console.error(err) 
  } finally { 
    loading.value = false 
  }
}

onMounted(fetchContacts)
</script>

<style scoped>
.contact-view { 
  max-width: 1240px; 
  margin: 0 auto; 
  padding: 0 var(--space-lg) var(--space-lg); /* 상단 패딩 제거 */
}

/* --- Fixed Header Area --- */
.fixed-top-area {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-main);
  padding-top: var(--space-lg); /* 컨테이너 패딩 이전 */
  padding-bottom: 2px;
}

/* --- View Header --- */
/* --- View Header Styles (Synced) --- */
.view-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: var(--space-lg);
  padding: var(--space-md) var(--space-lg) 0;
  height: 60px;
}

.header-left { display: flex; align-items: center; gap: 24px; }
.nav-icon-btn {
  width: 54px; height: 54px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.nav-icon-btn:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  transform: scale(1.05);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.glass-btn {
  padding: 12px 20px; border-radius: 14px;
  font-weight: 700; font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; gap: 10px;
  transition: all 0.3s; cursor: pointer;
}
.glass-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: #3b82f6; color: white;
  transform: translateY(-2px);
}

.glass-btn.refresh.spinning .icon {
  display: inline-block;
  animation: rotate 1s linear infinite;
  color: #10b981;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.view-badge {
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  color: #6366f1;
  font-weight: 800;
  margin: 0;
}

.view-title { 
  font-size: 1.8rem; 
  font-weight: 800; 
  color: #ffffff; 
  margin: 0; 
  letter-spacing: -0.03em;
}

/* --- Contact Grid --- */
.contact-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); 
  gap: var(--space-lg); 
}

.contact-card {
  background: #1e293b; 
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px; /* 8px 통일 */
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.contact-card:hover { 
  transform: translateY(-2px); 
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
}

.card-content {
  padding: 24px;
}

.header-row {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.avatar-box {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #1e40af, #3b82f6); /* Deep Sapphire to Blue Gradient */
  border-radius: 8px; /* 8px 통일 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 800;
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(30, 64, 175, 0.2); /* 은은한 그림자로 조정 */
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.user-name {
  font-size: 1.4rem;
  font-weight: 800;
  color: #ffffff;
}

.user-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #94a3b8;
}

.user-dept {
  font-size: 1rem;
  color: #cbd5e1;
  font-weight: 500;
}

.phone-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.phone-icon {
  width: 18px;
  height: 18px;
  color: #fb7185; /* Soft Red/Rose Icon like image */
}

.phone-number {
  font-size: 1.25rem;
  font-weight: 800;
  color: #2dd4bf; /* Emerald/Cyan - much better than fluorescent yellow */
  text-decoration: none;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: -0.02em;
}

.task-badge-row {
  margin-top: 8px;
}

.task-badge {
  font-size: 0.85rem;
  font-weight: 700;
  color: #818cf8; /* Soft Purple/Blue Badge */
  background: rgba(129, 140, 248, 0.1);
  padding: 4px 12px;
  border-radius: 6px;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
  margin: 20px 0;
}

.description-row {
  min-height: 48px;
}

.task-description {
  font-size: 0.95rem;
  color: #94a3b8;
  line-height: 1.6;
  font-weight: 500;
}

.loading-state { text-align: center; padding: 120px 0; color: #94a3b8; }
.modern-loader { 
  width: 40px; height: 40px; 
  border: 3px solid rgba(255, 255, 255, 0.1); 
  border-top-color: #6366f1; 
  border-radius: 50%; 
  animation: spin 1s linear infinite; 
  margin: 0 auto 20px; 
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .contact-grid { grid-template-columns: 1fr; }
}
</style>
