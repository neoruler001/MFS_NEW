<template>
  <div class="summary-view">
    <div class="fixed-top-area">
      <header class="view-header">
        <div class="header-left">
          <button @click="router.push('/')" class="nav-icon-btn home" title="홈으로">
            <span class="icon">🏠</span>
          </button>
          <div class="title-group">
            <p class="view-badge">CORPORATE CARD SUMMARY</p>
            <h2 class="view-title">법인카드 요약 현황</h2>
          </div>
        </div>
        <div class="header-right">
          <button class="glass-btn refresh" @click="fetchUsages" :class="{ spinning: loading }">
            <span class="icon">↻</span>
            <span class="label">새로고침</span>
          </button>
          <button @click="router.back()" class="glass-btn back" title="뒤로가기">
            <span class="icon">←</span>
            <span class="label">뒤로가기</span>
          </button>
        </div>
      </header>

      <!-- 필터 바 -->
      <div class="filter-bar-container animate-fade-in">
        <div class="filter-bar">
          <div class="filter-section">
            <span class="filter-label">조회 기간</span>
            <div class="period-btn-group">
              <button class="period-btn" :class="{ active: activePeriod === 'thisMonth' }" @click="setPeriod('thisMonth')">당월</button>
              <button class="period-btn" :class="{ active: activePeriod === 'lastMonth' }" @click="setPeriod('lastMonth')">전월</button>
              <button class="period-btn" :class="{ active: activePeriod === '3months' }" @click="setPeriod('3months')">최근 3개월</button>
            </div>
            <div class="date-range-box">
              <input type="date" v-model="filterParams.frDate" class="modern-input" @click="$event.target.showPicker()" />
              <span class="range-sep">~</span>
              <input type="date" v-model="filterParams.toDate" class="modern-input" @click="$event.target.showPicker()" />
            </div>
          </div>
          
          <div class="filter-actions">
            <button class="action-btn btn-primary" @click="applyFilter">
              <span class="icon">🔍</span>
              조회하기
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>데이터를 집계 중입니다...</p>
    </div>
    
    <div v-else class="summary-content animate-slide-up">
      <!-- 최상단 요약 카드 (Bento Grid 스타일) -->
      <div class="summary-cards">
        <div class="bento-card total-amount-card">
          <div class="card-icon">💰</div>
          <div class="card-content">
            <p class="card-label">총 사용 금액</p>
            <h3 class="card-value">{{ formatAmount(totalAmount) }}<small>원</small></h3>
          </div>
        </div>
        <div class="bento-card total-count-card">
          <div class="card-icon">🧾</div>
          <div class="card-content">
            <p class="card-label">총 사용 건수</p>
            <h3 class="card-value">{{ totalCount }}<small>건</small></h3>
          </div>
        </div>
        <div class="bento-card top-account-card">
          <div class="card-icon">🏆</div>
          <div class="card-content">
            <p class="card-label">최대 지출 계정</p>
            <h3 class="card-value truncate" :title="topAccountName">{{ topAccountName || '-' }}</h3>
            <p class="card-sub-value" v-if="topAccountAmt > 0">{{ formatAmount(topAccountAmt) }} 원</p>
          </div>
        </div>
      </div>

      <!-- 비용계정별 요약 테이블 -->
      <div class="summary-table-section">
        <div class="section-header">
          <h3>비용계정별 집계 내역</h3>
        </div>
        <div class="table-container">
          <table class="modern-table">
            <thead>
              <tr>
                <th>순위</th>
                <th class="text-left">비용계정 (적요/분류)</th>
                <th class="text-right">사용 건수</th>
                <th class="text-right">총 금액</th>
                <th>비율</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in summaryData" :key="idx" class="table-row">
                <td><span class="rank-badge" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</span></td>
                <td class="text-left font-bold">{{ item.accountName }}</td>
                <td class="text-right clickable-count" @click="openDetailsModal(item)" title="상세내역 보기">
                  <span class="count-val">{{ item.count }}</span> 건
                </td>
                <td class="text-right font-mono highlight-amt">{{ formatAmount(item.amount) }} 원</td>
                <td>
                  <div class="progress-bar-container">
                    <div class="progress-fill" :style="{ width: item.percentage + '%' }"></div>
                    <span class="progress-text">{{ item.percentage }}%</span>
                  </div>
                </td>
              </tr>
              <tr v-if="summaryData.length === 0">
                <td colspan="5" class="empty-row">조회된 내역이 없습니다.</td>
              </tr>
            </tbody>
            <tfoot v-if="summaryData.length > 0">
              <tr>
                <td colspan="2" class="text-right font-bold">합계</td>
                <td class="text-right font-bold">{{ totalCount }} 건</td>
                <td class="text-right font-bold text-primary">{{ formatAmount(totalAmount) }} 원</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>

    <!-- 상세 내역 모달 -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="showDetailsModal = false">
      <div class="modal-content details-modal" @click.stop>
        <div class="classic-header">
          <h3>{{ activeAccountName }} - 상세 내역</h3>
          <button @click="showDetailsModal = false" class="classic-close">✕</button>
        </div>
        <div class="classic-body modal-scroll">
          <div class="usage-list">
            <div v-for="(uItem, idx) in activeAccountDetails" :key="idx" class="usage-card">
              <div class="card-info">
                <div class="top-row">
                  <span class="merchant-name">{{ uItem.AFFI_NAME }}</span>
                  <span class="status-badge" :class="getStatusClass(uItem.DOC_STATUS)">
                    {{ uItem.DOC_STATUS || '비용 처리 전' }}
                  </span>
                </div>
                <div class="bottom-row">
                  <span class="date">{{ formatFullDate(uItem.APPR_DATE) }}</span>
                  <span class="card-num">{{ uItem.KIND }} ({{ uItem.CARD_NUMC ? uItem.CARD_NUMC.slice(-4) : '' }})</span>
                </div>
              </div>
              <div class="card-price">
                <div class="amount">{{ formatAmount(uItem.KRW_AMT) }}<small>원</small></div>
                <div class="user">{{ uItem.NAME }}</div>
                <div class="auth-no">AUTH: {{ uItem.APPR_NUMC }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const rawUsages = ref([])
const activePeriod = ref('')

const filterParams = ref({
  frDate: '',
  toDate: ''
})

const setPeriod = (type) => {
  activePeriod.value = type
  const today = new Date()
  
  if (type === 'thisMonth') {
    const f = new Date(today.getFullYear(), today.getMonth(), 1)
    filterParams.value.frDate = f.toISOString().slice(0, 10)
    filterParams.value.toDate = today.toISOString().slice(0, 10)
  } else if (type === 'lastMonth') {
    const f = new Date(today.getFullYear(), today.getMonth() - 1, 1)
    const l = new Date(today.getFullYear(), today.getMonth(), 0)
    filterParams.value.frDate = f.toISOString().slice(0, 10)
    filterParams.value.toDate = l.toISOString().slice(0, 10)
  } else if (type === '3months') {
    const f = new Date(today.getFullYear(), today.getMonth() - 2, 1)
    filterParams.value.frDate = f.toISOString().slice(0, 10)
    filterParams.value.toDate = today.toISOString().slice(0, 10)
  }
}

const applyFilter = () => {
  fetchUsages()
}

const fetchUsages = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/cards/usages', {
      params: {
        fr_date: filterParams.value.frDate ? filterParams.value.frDate.replace(/-/g, "") : "",
        to_date: filterParams.value.toDate ? filterParams.value.toDate.replace(/-/g, "") : "",
        pi_status: "A" // 전체 내역 기준
      }
    })
    
    let data = res.data
    if (data && !Array.isArray(data)) {
      data = [data]
    }
    rawUsages.value = data || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 데이터 집계 로직 (비용계정 = DOC_SGTXT 또는 DOCPR(업무코드))
const summaryData = computed(() => {
  const grouped = {}
  let totalAmt = 0

  rawUsages.value.forEach(item => {
    // 비용계정 기준: 1. 적요(DOC_SGTXT) -> 2. 업무코드(DOCPR) -> 3. 미지정
    const accountName = item.DOC_SGTXT || (item.DOCPR ? `유형코드: ${item.DOCPR}` : '미지정 계정')
    const amt = Number(item.KRW_AMT) || 0

    if (!grouped[accountName]) {
      grouped[accountName] = { accountName, count: 0, amount: 0 }
    }
    grouped[accountName].count += 1
    grouped[accountName].amount += amt
    totalAmt += amt
  })

  // 배열로 변환 후 금액 기준 내림차순 정렬
  const resultArr = Object.values(grouped).sort((a, b) => b.amount - a.amount)
  
  // 백분율 계산
  return resultArr.map(item => {
    item.percentage = totalAmt > 0 ? ((item.amount / totalAmt) * 100).toFixed(1) : 0
    return item
  })
})

const totalAmount = computed(() => summaryData.value.reduce((acc, curr) => acc + curr.amount, 0))
const totalCount = computed(() => summaryData.value.reduce((acc, curr) => acc + curr.count, 0))
const topAccountName = computed(() => summaryData.value.length > 0 ? summaryData.value[0].accountName : '')
const topAccountAmt = computed(() => summaryData.value.length > 0 ? summaryData.value[0].amount : 0)

const formatAmount = (val) => val ? new Intl.NumberFormat('ko-KR').format(val) : '0'

// 팝업 관련 상태 및 함수
const showDetailsModal = ref(false)
const activeAccountDetails = ref([])
const activeAccountName = ref('')

const openDetailsModal = (item) => {
  activeAccountName.value = item.accountName
  activeAccountDetails.value = rawUsages.value.filter(u => {
    const accName = u.DOC_SGTXT || (u.DOCPR ? `유형코드: ${u.DOCPR}` : '미지정 계정')
    return accName === item.accountName
  })
  showDetailsModal.value = true
}

const formatFullDate = (val) => (val && val.length >= 8) ? `${val.substring(0,4)}-${val.substring(4,6)}-${val.substring(6,8)}` : '-'

const getStatusClass = (s) => {
  if (!s || s === '미처리' || s === '비용 처리 전') return 's-ready'
  if (s.includes('진행') || s.includes('결재 중')) return 's-pending'
  if (s.includes('완료')) return 's-done'
  if (s.includes('반려') || s.includes('취소')) return 's-rejected'
  return 's-wait'
}

onMounted(() => {
  setPeriod('thisMonth')
  fetchUsages()
})
</script>

<style scoped>
.summary-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg) var(--space-lg);
}

/* --- View Header (CardUsageView와 통일) --- */
.view-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: var(--space-lg);
  padding-top: var(--space-md);
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

.header-right { display: flex; align-items: center; gap: 12px; }

.view-title { 
  font-size: 1.75rem; 
  font-weight: 800; 
  color: #ffffff; 
  margin: 0; 
  letter-spacing: -0.02em;
}

.view-badge { 
  font-size: 0.75rem; 
  color: var(--color-primary); 
  font-weight: 700; 
  margin-bottom: 4px; 
  letter-spacing: 0.1em;
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

.fixed-top-area {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-main);
  padding-top: var(--space-lg);
  padding-bottom: 4px;
}

/* --- Filter Bar --- */
.filter-bar-container {
  margin-bottom: var(--space-xl);
}

.filter-bar {
  background: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(16px);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--border-strong);
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.4);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-muted);
}

.period-btn-group {
  display: flex;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 10px;
  padding: 4px;
  border: 1px solid var(--border-subtle);
}

.period-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-dim);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.period-btn:hover { color: white; }
.period-btn.active {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.date-range-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.modern-input {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--border-subtle);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s;
}

.modern-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.range-sep { color: var(--text-muted); }

.action-btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

/* --- Loading --- */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: var(--text-muted);
}
.spinner {
  width: 40px; height: 40px;
  border: 4px solid rgba(255,255,255,0.1);
  border-left-color: var(--color-primary);
  border-radius: 50%;
  animation: rotate 1s linear infinite;
  margin-bottom: 16px;
}

/* --- Summary Content --- */
.summary-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.bento-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);
}

.bento-card:hover {
  transform: translateY(-5px);
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 15px 35px -5px rgba(0,0,0,0.3);
}

.total-amount-card .card-icon { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid rgba(59,130,246,0.3); }
.total-count-card .card-icon { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.top-account-card .card-icon { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }

.card-icon {
  width: 64px; height: 64px;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.card-content { flex: 1; min-width: 0; }
.card-label { font-size: 0.9rem; color: var(--text-muted); font-weight: 600; margin-bottom: 4px; }
.card-value { font-size: 1.8rem; font-weight: 800; color: white; margin: 0; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.05em; }
.card-value small { font-size: 1rem; color: var(--text-dim); margin-left: 4px; font-weight: 600; }
.card-sub-value { font-size: 0.9rem; color: #10b981; font-weight: 600; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* --- Table Section --- */
.summary-table-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 1.4rem;
  font-weight: 800;
  color: white;
  margin: 0;
}

.table-container {
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.modern-table th {
  padding: 16px;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-strong);
  background: rgba(15, 23, 42, 0.4);
}

.modern-table td {
  padding: 16px;
  font-size: 1rem;
  color: #e2e8f0;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

.modern-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.modern-table tfoot td {
  background: rgba(59, 130, 246, 0.05);
  border-top: 2px solid var(--border-strong);
  border-bottom: none;
  font-size: 1.1rem;
}

.text-left { text-align: left; }
.text-right { text-align: right; }
.text-center { text-align: center; }
.font-bold { font-weight: 700; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.text-primary { color: #3b82f6 !important; }

.highlight-amt {
  color: white;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px; height: 28px;
  background: #334155;
  color: white;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 800;
}
.rank-1 { background: #fbbf24; color: #78350f; }
.rank-2 { background: #94a3b8; color: #0f172a; }
.rank-3 { background: #b45309; color: white; }

.empty-row {
  text-align: center;
  padding: 40px !important;
  color: var(--text-muted) !important;
  font-size: 1.1rem !important;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 150px;
}

.progress-fill {
  height: 8px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 4px;
}

.progress-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 600;
  width: 45px;
  text-align: right;
}

/* Animations */
.animate-fade-in { animation: fadeIn 0.6s ease-out; }
.animate-slide-up { animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --- Modal & Usage Card Styles --- */
.clickable-count {
  cursor: pointer;
  transition: all 0.2s;
}

.clickable-count:hover .count-val {
  color: #3b82f6;
  text-decoration: underline;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(2, 6, 23, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content.details-modal {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.classic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: rgba(15, 23, 42, 0.95);
  border-bottom: 1px solid var(--border-strong);
}

.classic-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  color: white;
}

.classic-close {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s;
}

.classic-close:hover {
  color: white;
}

.modal-scroll {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Usage Card Styles from CardUsageView */
.usage-list { display: flex; flex-direction: column; gap: 1rem; }

.usage-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.2s ease;
}

.usage-card:hover {
  background: #243147;
  border-color: var(--border-strong);
}

.card-info { flex: 1; }
.top-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }

.merchant-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
}

.status-badge {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 0.02em;
}

.s-ready { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); }
.s-pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); }
.s-done { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.s-rejected { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }
.s-wait { background: #334155; color: #94a3b8; }

.bottom-row {
  font-size: 0.85rem;
  color: var(--text-dim);
  display: flex;
  gap: 20px;
}

.card-price {
  width: 180px;
  text-align: right;
  border-left: 1px solid var(--border-subtle);
  padding-left: 20px;
}

.amount {
  font-size: 1.4rem;
  font-weight: 800;
  color: #ffffff;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: -0.05em;
}

.user { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; font-weight: 600; }
.auth-no { font-size: 0.7rem; color: var(--text-muted); margin-top: 2px; }

/* --- Responsive Media Queries --- */
@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    height: auto;
    gap: 16px;
    padding-bottom: 16px;
  }
  
  .header-left {
    width: 100%;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .date-range-box {
    flex-direction: column;
    align-items: stretch;
  }

  .modern-input {
    width: 100%;
    box-sizing: border-box;
  }
  
  .range-sep {
    text-align: center;
  }

  .summary-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .bento-card {
    padding: 16px;
  }

  .card-value {
    font-size: 1.5rem;
  }

  .summary-table-section {
    padding: 16px;
  }
  
  .modern-table th, .modern-table td {
    padding: 12px 8px;
    font-size: 0.85rem;
  }

  .progress-bar-container {
    width: 80px;
  }
  
  .usage-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
  }

  .card-price {
    width: 100%;
    text-align: left;
    border-left: none;
    border-top: 1px solid var(--border-subtle);
    padding-left: 0;
    padding-top: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .card-price .amount {
    font-size: 1.2rem;
  }
  
  .card-price .user, .card-price .auth-no {
    margin-top: 0;
  }
  
  .classic-header {
    padding: 16px;
  }
  
  .modal-scroll {
    padding: 16px;
  }
}
</style>
