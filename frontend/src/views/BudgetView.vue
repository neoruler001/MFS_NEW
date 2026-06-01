<template>
  <div class="budget-view">
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
          <div class="header-left">
            <button @click="router.push('/')" class="nav-icon-btn home" title="홈으로">
              <span class="icon">🏠</span>
            </button>
            <div class="title-group">
              <span class="company-badge">BUDGET MANAGEMENT</span>
              <h2 class="view-title">예산 집행 현황</h2>
            </div>
          </div>
          
          <div class="header-actions">
            <button class="glass-btn refresh" @click="fetchBudget" :class="{ spinning: loading }">
              <span class="icon">↻</span>
              <span class="label">새로고침</span>
            </button>
            <button @click="router.back()" class="glass-btn back" title="뒤로가기">
              <span class="icon">←</span>
              <span class="label">뒤로가기</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Loading State -->
      <div v-if="loading" class="state-container animate-fade-in">
        <div class="premium-loader"></div>
        <p class="state-text">실시간 예산 데이터를 집계 중입니다...</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="budgets.length === 0" class="state-container animate-fade-in">
        <div class="empty-icon">📂</div>
        <p class="state-text">조회된 예산 데이터가 없습니다.</p>
      </div>

      <!-- Budget List Section: Grouped by Company -->
      <section v-else class="budget-section">
        <div v-for="(group, companyName) in groupedBudgets" :key="companyName" class="company-group animate-fade-in">
          <!-- Company Group Header -->
          <div class="group-header">
            <div class="group-title-wrapper">
              <span class="group-dot"></span>
              <h3 class="group-company-name">{{ companyName }}</h3>
              <span class="group-count">{{ group.length }}개 항목</span>
            </div>
            <div class="group-line"></div>
          </div>
          
          <!-- Grid for this company's cards -->
          <div class="budget-grid">
            <div v-for="(item, index) in group" 
                 :key="index" 
                 class="budget-card"
                 :class="'animate-stagger-' + ((index % 4) + 1)">
              <div class="card-glass-content">
                <!-- Card Header -->
                <div class="card-top">
                  <div class="header-main-info">
                    <div class="sub-info-row">
                      <span class="info-text">
                        {{ item.processedDetails }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Metrics Grid -->
                <div class="metrics-grid">
                  <div class="metric-box">
                    <span class="metric-label">총 예산</span>
                    <span class="metric-value">{{ formatAmount(item.PLAMT || 0) }}</span>
                  </div>
                  <div class="metric-box">
                    <span class="metric-label">사용금액</span>
                    <span class="metric-value usage">{{ formatAmount(item.ATAMT || 0) }}</span>
                  </div>
                  <div class="metric-box highlight">
                    <span class="metric-label">잔여예산</span>
                    <span class="metric-value balance" :class="{ 'zero': calculateProgress(item) >= 100 }">
                      {{ formatAmount(item.RMAMT || 0) }}
                    </span>
                  </div>
                </div>

                <!-- Progress Section -->
                <div class="progress-section">
                  <div class="progress-info">
                    <span class="progress-label">집행률</span>
                    <span class="progress-percent" 
                          :class="{ 'warning': calculateProgress(item) > 80, 'critical': calculateProgress(item) >= 100 }">
                      {{ calculateProgress(item) }}%
                    </span>
                  </div>
                  <div class="progress-track">
                    <div class="progress-fill" 
                         :style="{ width: calculateProgress(item) + '%' }"
                         :class="{ 'warning-fill': calculateProgress(item) > 80, 'critical-fill': calculateProgress(item) >= 100 }">
                      <div class="progress-glow"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="system-footer animate-fade-in">
        <div class="footer-line"></div>
        <p>© 2026 HD현대E&T Budget Intelligence System</p>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const budgets = ref([])
const loading = ref(true)

// 회사별 그룹핑 및 데이터 가공 로직
const groupedBudgets = computed(() => {
  const groups = {}
  
  budgets.value.forEach(item => {
    const processed = processBudgetData(item)
    const company = processed.company
    
    if (!groups[company]) {
      groups[company] = []
    }
    
    groups[company].push({
      ...item,
      processedDetails: processed.details
    })
  })
  
  return groups
})

const fetchBudget = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/budget/budget')
    const data = res.data
    let targetData = []

    if (data.TE_BUDGET) {
      targetData = data.TE_BUDGET
    } else if (Array.isArray(data)) {
      targetData = data
    } else {
      // 리스트가 있는 키를 찾아 할당하거나, 데이터 자체가 객체면 배열로 감쌈
      for (let key in data) {
        if (Array.isArray(data[key])) {
          targetData = data[key]
          break
        }
      }
      if (targetData.length === 0 && data && Object.keys(data).length > 0) {
        targetData = [data]
      }
    }
    
    // 최종 배열 보장
    budgets.value = Array.isArray(targetData) ? targetData : []
  } catch (err) {
    console.error('Failed to fetch budget', err)
  } finally {
    setTimeout(() => { loading.value = false }, 500)
  }
}

// 데이터 가공 함수
const processBudgetData = (item) => {
  let company = item.BUKRS_NAME || 'HD HYUNDAI'
  let details = `${item.NAME || ''}-${item.TITLE || ''}-${item.KOSTL_NAME || ''}`
  
  let targetString = ''
  for (const key in item) {
    const val = String(item[key] || '')
    if (val.includes('에이치디') && val.includes('-')) {
      targetString = val
      break
    }
  }

  if (targetString) {
    let cleanStr = targetString.replace(/^[ \-/]+|[ \-/]+$/g, '').trim()
    
    if (cleanStr.includes('-')) {
      const parts = cleanStr.split('-').map(p => p.trim()).filter(p => p.length > 0)
      
      if (parts.length >= 2) {
        company = parts[0]
        details = parts.slice(1).join('-')
      } else if (parts.length === 1) {
        company = parts[0]
        details = ''
      }
    } else {
      company = cleanStr
      details = ''
    }
  }

  return { company, details }
}

const formatAmount = (val) => {
  if (val === undefined || val === null) return '0'
  return new Intl.NumberFormat('ko-KR').format(val)
}

const calculateProgress = (item) => {
  if (!item.PLAMT || item.PLAMT === 0) return 0
  const percent = (item.ATAMT / item.PLAMT) * 100
  return Math.min(Math.round(percent), 100)
}

onMounted(fetchBudget)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@500;700&display=swap');

.budget-view {
  min-height: 100vh;
  background-color: #020617;
  font-family: 'Outfit', sans-serif;
  color: #f8fafc;
  overflow-x: hidden;
  position: relative;
}

.background-blobs {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  overflow: hidden;
  z-index: 0;
}

.blob {
  position: absolute;
  width: 700px; height: 700px;
  filter: blur(140px);
  opacity: 0.1;
  border-radius: 50%;
  animation: move-blobs 30s infinite alternate;
}

.blob-1 { background: #10b981; top: -10%; right: -10%; }
.blob-2 { background: #3b82f6; bottom: -10%; left: -10%; animation-delay: -7s; }
.blob-3 { background: #8b5cf6; top: 40%; left: 30%; animation-delay: -15s; }

@keyframes move-blobs {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(80px, 150px) scale(1.1); }
  100% { transform: translate(-60px, -80px) scale(0.9); }
}

.main-container {
  position: relative;
  z-index: 1;
  max-width: 1150px; /* Neo의 요청에 따라 너비를 줄여 집중도 향상 */
  margin: 0 auto;
  padding: 40px 24px;
}

/* --- Grouping Styles --- */
.company-group {
  margin-bottom: 60px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.group-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  white-space: nowrap;
}

.group-dot {
  width: 10px;
  height: 10px;
  background: #3b82f6;
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.8);
}

.group-company-name {
  font-size: 1.8rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -0.02em;
  margin: 0;
}

.group-count {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  background: rgba(100, 116, 139, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
}

.group-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.3), transparent);
}

/* --- Executive Header --- */
.executive-header { margin-bottom: 40px; }
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  padding: 24px 32px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.4);
}

.header-left { display: flex; align-items: center; gap: 24px; }
.nav-icon-btn {
  width: 54px; height: 54px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; cursor: pointer;
  transition: all 0.3s;
}
.nav-icon-btn:hover { background: rgba(59, 130, 246, 0.2); border-color: #3b82f6; transform: scale(1.05); }

.company-badge {
  font-size: 0.7rem; font-weight: 800; color: #10b981;
  letter-spacing: 0.15em; text-transform: uppercase;
  background: rgba(16, 185, 129, 0.1);
  padding: 4px 12px; border-radius: 6px;
  margin-bottom: 6px; display: inline-block;
}
.view-title { font-size: 1.8rem; font-weight: 800; color: #ffffff; margin: 0; }

.header-actions { display: flex; gap: 12px; }
.glass-btn {
  padding: 12px 20px; border-radius: 14px;
  font-weight: 700; font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; gap: 10px;
  transition: all 0.3s; cursor: pointer;
}
.glass-btn:hover { background: rgba(255, 255, 255, 0.12); border-color: #3b82f6; color: white; transform: translateY(-2px); }

.glass-btn.refresh.spinning .icon { display: inline-block; animation: rotate 1s linear infinite; color: #10b981; }
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* --- Budget Grid --- */
.budget-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.budget-card {
  position: relative;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

.card-glass-content {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(20px);
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.budget-card:hover {
  transform: translateY(-8px);
  border-color: rgba(16, 185, 129, 0.4);
  box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.5);
}

.header-main-info { display: flex; flex-direction: column; gap: 8px; }
.sub-info-row { font-size: 1.1rem; font-weight: 600; color: #94a3b8; }

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  background: rgba(15, 23, 42, 0.3);
  padding: 24px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.03);
}

.metric-box { display: flex; flex-direction: column; gap: 6px; }
.metric-label { font-size: 0.85rem; font-weight: 700; color: #64748b; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 700; color: #f8fafc; }
.metric-value.usage { color: #f43f5e; }
.metric-box.highlight .metric-value.balance { font-size: 1.6rem; color: #10b981; }
.metric-value.balance.zero { color: #f43f5e; }

.progress-section { display: flex; flex-direction: column; gap: 12px; }
.progress-info { display: flex; justify-content: space-between; align-items: center; }
.progress-label { font-size: 0.9rem; font-weight: 600; color: #94a3b8; }
.progress-percent { font-size: 1.2rem; font-weight: 800; color: #10b981; }
.progress-percent.warning { color: #f59e0b; }
.progress-percent.critical { color: #f43f5e; }

.progress-track { height: 12px; background: rgba(0, 0, 0, 0.3); border-radius: 10px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05); }
.progress-fill {
  height: 100%; background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 10px; position: relative;
  transition: width 1.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.progress-fill.warning-fill { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.progress-fill.critical-fill { background: linear-gradient(90deg, #f43f5e, #fb7185); }
.progress-glow { position: absolute; top: 0; right: 0; bottom: 0; width: 20px; background: white; filter: blur(8px); opacity: 0.3; }

/* --- State Containers --- */
.state-container { text-align: center; padding: 100px 0; background: rgba(255, 255, 255, 0.02); border-radius: 32px; border: 1px dashed rgba(255, 255, 255, 0.1); }
.state-text { font-size: 1.1rem; color: #94a3b8; margin-top: 20px; }
.premium-loader { width: 50px; height: 50px; border: 4px solid rgba(59, 130, 246, 0.1); border-top-color: #3b82f6; border-radius: 50%; margin: 0 auto; animation: rotate 1s linear infinite; }
.empty-icon { font-size: 4rem; opacity: 0.2; }

.system-footer { margin-top: 40px; text-align: center; }
.footer-line { height: 1px; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent); margin-bottom: 24px; }
.system-footer p { font-size: 0.85rem; color: #64748b; font-weight: 500; }

.animate-fade-in { animation: fadeIn 0.8s ease-out forwards; }
.animate-stagger-1 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.1s both; }
.animate-stagger-2 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.2s both; }
.animate-stagger-3 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.3s both; }
.animate-stagger-4 { animation: slideInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) 0.4s both; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1024px) { .budget-grid { grid-template-columns: 1fr; } }
@media (max-width: 640px) { .header-content { flex-direction: column; gap: 20px; align-items: flex-start; } .metrics-grid { grid-template-columns: 1fr; } }
</style>
