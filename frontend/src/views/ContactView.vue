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

          <!-- 상단: 아바타 + 기본정보 -->
          <div class="header-row">
            <div class="avatar-box">
              {{ item.NAME ? item.NAME[0] : '?' }}
            </div>
            <div class="user-info">
              <!-- 성명 + 직위 -->
              <div class="name-row">
                <span class="user-name">{{ item.NAME }}</span>
                <span v-if="item.TITLE" class="user-title">{{ item.TITLE }}</span>
              </div>
              <!-- 소속 -->
              <div v-if="item.DIVISION" class="user-dept">
                <span class="info-label">소속</span>
                <span>{{ item.DIVISION }}</span>
              </div>
              <!-- 전화번호 -->
              <div class="phone-row">
                <svg class="phone-icon" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M6.62,10.79C8.06,13.62 10.38,15.94 13.21,17.38L15.41,15.18C15.69,14.9 16.08,14.82 16.43,14.93C17.55,15.3 18.75,15.5 20,15.5A1,1 0 0,1 21,16.5V20A1,1 0 0,1 20,21A17,17 0 0,1 3,4A1,1 0 0,1 4,3H7.5A1,1 0 0,1 8.5,4C8.5,5.25 8.7,6.45 9.07,7.57C9.18,7.92 9.1,8.31 8.82,8.59L6.62,10.79Z" />
                </svg>
                <a :href="'tel:' + item.TEL" class="phone-number">{{ item.TEL }}</a>
              </div>
            </div>
          </div>

          <!-- 업무 목록 -->
          <template v-if="hasTasks(item)">
            <div class="divider"></div>
            <div class="tasks-section">
              <!-- 업무 섹션 헤더: 라벨 + WORK 구분 태그 -->
              <div class="tasks-label">
                <i class="tasks-icon">📋</i>
                <!-- <span>업무</span> -->
                <span v-if="item.WORK" class="work-type-badge">{{ item.WORK }}</span>
              </div>
              <!-- TASKS 배열 형식 (SAP/MSSQL 공통) -->
              <template v-if="item.TASKS && item.TASKS.length > 0">
                <div
                  v-for="(task, ti) in item.TASKS"
                  :key="ti"
                  class="task-item"
                >
                  <span class="task-bullet">▸</span>
                  <div class="task-texts">
                    <span class="task-name">{{ task.name }}</span>
                    <span v-if="task.desc && task.desc !== task.name" class="task-desc">{{ task.desc }}</span>
                  </div>
                </div>
              </template>
              <!-- 레거시 단일 필드 형식 (하위호환) -->
              <template v-else>
                <div v-if="item.SYSTEM_NAME" class="task-item">
                  <span class="task-bullet">▸</span>
                  <div class="task-texts">
                    <span class="task-name">{{ item.SYSTEM_NAME }}</span>
                    <span v-if="item.SYSTEM_DESC && item.SYSTEM_DESC !== item.SYSTEM_NAME" class="task-desc">{{ item.SYSTEM_DESC }}</span>
                  </div>
                </div>
              </template>
            </div>
          </template>

          <!-- 업무가 없을 때: WORK 구분 태그만 표시 -->
          <template v-else>
            <div class="divider"></div>
            <div class="no-task-row">
              <span class="work-type-badge">{{ item.WORK || item.REMARK || '업무' }}</span>
            </div>
          </template>

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

const hasTasks = (item) => {
  if (item.TASKS && item.TASKS.length > 0) return true
  if (item.SYSTEM_NAME && item.SYSTEM_NAME.trim()) return true
  return false
}

const fetchContacts = async () => {
  loading.value = true
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
  padding: 0 var(--space-lg) var(--space-lg);
}

/* --- Fixed Header Area --- */
.fixed-top-area {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-main);
  padding-top: var(--space-lg);
  padding-bottom: 2px;
}

/* --- View Header --- */
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
  border-radius: 8px;
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

/* --- 상단 헤더 행 --- */
.header-row {
  display: flex;
  gap: 20px;
  margin-bottom: 0;
}

.avatar-box {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 800;
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(30, 64, 175, 0.2);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
  flex: 1;
}

/* 성명 + 직위 */
.name-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.user-name {
  font-size: 1.4rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.2;
}

.user-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: #94a3b8;
  white-space: nowrap;
}

/* 소속 */
.user-dept {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: #cbd5e1;
  font-weight: 500;
}

.info-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #6366f1;
  background: rgba(99, 102, 241, 0.12);
  padding: 2px 7px;
  border-radius: 4px;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

/* 전화번호 */
.phone-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.phone-icon {
  width: 18px;
  height: 18px;
  color: #fb7185;
  flex-shrink: 0;
}

.phone-number {
  font-size: 1.15rem;
  font-weight: 800;
  color: #2dd4bf;
  text-decoration: none;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: -0.02em;
}

.phone-number:hover {
  color: #5eead4;
  text-decoration: underline;
}

/* --- 구분선 --- */
.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.07);
  margin: 16px 0;
}

/* --- 업무 목록 --- */
.tasks-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tasks-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

/* 업무/전산 구분 태그 */
.work-type-badge {
  font-size: 0.72rem;
  font-weight: 700;
  color: #10b981;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: 0.02em;
  text-transform: none;
  white-space: nowrap;
}

.tasks-icon {
  font-style: normal;
  font-size: 0.9rem;
}

.task-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border-left: 2px solid rgba(99, 102, 241, 0.4);
  transition: background 0.2s;
}

.task-item:hover {
  background: rgba(99, 102, 241, 0.08);
  border-left-color: #6366f1;
}

.task-bullet {
  color: #6366f1;
  font-size: 0.8rem;
  margin-top: 2px;
  flex-shrink: 0;
}

.task-texts {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.task-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: #e2e8f0;
  line-height: 1.4;
}

.task-desc {
  font-size: 0.82rem;
  color: #94a3b8;
  line-height: 1.4;
}

/* 업무 없을 때 배지 */
.no-task-row {
  padding: 4px 0;
}

.task-badge {
  font-size: 0.85rem;
  font-weight: 700;
  color: #818cf8;
  background: rgba(129, 140, 248, 0.1);
  padding: 4px 12px;
  border-radius: 6px;
}

/* --- Loading --- */
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
  .view-title { font-size: 1.4rem; }
}
</style>
