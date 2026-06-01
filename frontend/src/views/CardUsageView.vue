<template>
  <div class="usage-view">
    <div class="fixed-top-area">
      <header class="view-header">
        <div class="header-left">
          <button @click="router.push('/')" class="nav-icon-btn home" title="홈으로">
            <span class="icon">🏠</span>
          </button>
          <div class="title-group">
            <p class="view-badge">CORPORATE CARD LEDGER</p>
            <h2 class="view-title">법인카드 이용내역</h2>
          </div>
        </div>
        <div class="header-right">
          <button class="glass-btn refresh" @click="fetchUsages" :class="{ spinning: loading }">
            <span class="icon">↻</span>
            <span class="label">새로고침</span>
          </button>
          <button class="filter-trigger-btn" @click="showFilterModal = true">
            <span class="icon">🔍</span>
            <span class="label">필터 검색</span>
          </button>
          <button @click="router.back()" class="glass-btn back" title="뒤로가기">
            <span class="icon">←</span>
            <span class="label">뒤로가기</span>
          </button>
        </div>
      </header>

      <div class="action-bar-container">
        <div class="action-bar">
          <div class="selection-status">
            <span v-if="selectedItems.length > 0">
              <strong>{{ selectedItems.length }}</strong>건 선택 ({{ formatAmount(selectedTotalAmt) }}원)
            </span>
            <span v-else class="placeholder">항목을 선택하여 업무를 시작하세요.</span>
          </div>
          <div class="btn-group">
            <button class="action-btn btn-primary" @click="processExpenses" :disabled="selectedItems.length === 0">비용처리</button>
            <button class="action-btn btn-outline" @click="cancelProcessing" :disabled="selectedItems.length === 0">처리취소</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>데이터를 로딩 중입니다...</p>
    </div>
    
    <div v-else class="usage-list">
      <div v-for="(item, idx) in usages" :key="idx" 
           class="usage-card" 
           :class="{ 'selected': selectedItems.includes(idx) }"
           @click="toggleSelection(idx)">
        
        <div class="card-check">
          <input type="checkbox" :value="idx" v-model="selectedItems" @click.stop />
        </div>

        <div class="card-info">
          <div class="top-row">
            <span class="merchant-name">{{ item.AFFI_NAME }}</span>
            <span class="status-badge clickable" :class="getStatusClass(item.DOC_STATUS)" @click.stop="openProcessModal(item)">
              {{ item.DOC_STATUS || '비용 처리 전' }}
            </span>
          </div>
          <div class="bottom-row">
            <span class="date">{{ formatFullDate(item.APPR_DATE) }}</span>
            <span class="card-num">{{ item.KIND }} ({{ item.CARD_NUMC.slice(-4) }})</span>
          </div>
        </div>

        <div class="card-price" @click.stop="openReceiptModal(item)">
          <div class="amount">{{ formatAmount(item.KRW_AMT) }}<small>원</small></div>
          <div class="user">{{ item.NAME }}</div>
          <div class="auth-no">AUTH: {{ item.APPR_NUMC }}</div>
        </div>
      </div>
      <div v-if="usages.length === 0" class="empty-msg">조회 결과가 없습니다.</div>
    </div>

    <!-- 1. 상세 필터 모달 (Modern Redesign) -->
    <div v-if="showFilterModal" class="modal-overlay" @click="showFilterModal = false">
      <div class="modal-content filter-modern" @click.stop>
        <header class="classic-header">
          <h3>상세 필터 설정</h3>
          <button @click="showFilterModal = false" class="classic-close">✕</button>
        </header>
        
        <div class="filter-body">
          <!-- 소유자 & 카드번호 섹션 -->
          <div class="filter-row">
            <div class="filter-group">
              <label>소유자</label>
              <select v-model="filterParams.cardOwner" class="modern-input">
                <option value="">전체 소유자</option>
                <option v-for="o in knownOwners" :key="o.PERNR" :value="o.PERNR">{{ o.NAME }} ({{ o.PERNR }})</option>
              </select>
            </div>
            <div class="filter-group">
              <label>카드번호</label>
              <select v-model="filterParams.cardNum" class="modern-input">
                <option value="">전체 카드</option>
                <option v-for="c in knownCards" :key="c.CARD_NUMC" :value="c.CARD_NUMC">{{ c.CARD_NUMC }} ({{ c.KIND }})</option>
              </select>
            </div>
          </div>

          <!-- 조회 기간 섹션 -->
          <div class="filter-section">
            <label>조회 기간</label>
            <div class="period-btn-group">
              <button v-for="p in [{v:'yesterday',l:'어제'},{v:'1week',l:'1주'},{v:'thisMonth',l:'당월'},{v:'lastMonth',l:'전월'}]" 
                      :key="p.v"
                      class="period-btn" :class="{ active: activePeriod === p.v }" 
                      @click="setPeriod(p.v)">{{ p.l }}</button>
            </div>
            <div class="date-range-box">
              <input type="date" v-model="filterParams.frDate" class="modern-input" />
              <span class="range-sep">~</span>
              <input type="date" v-model="filterParams.toDate" class="modern-input" />
            </div>
          </div>

          <!-- 처리 상태 섹션 -->
          <div class="filter-section">
            <label>처리 상태</label>
            <div class="status-btn-group">
              <button v-for="s in [{v:'A',l:'전체'},{v:'C',l:'처리 완료'},{v:'P',l:'미처리'}]" 
                      :key="s.v"
                      class="status-tab-btn" :class="{ active: filterParams.status === s.v }" 
                      @click="filterParams.status = s.v">{{ s.l }}</button>
            </div>
          </div>
        </div>

        <footer class="filter-footer">
          <button class="apply-filter-btn" @click="applyFilter">데이터 조회하기</button>
        </footer>
      </div>
    </div>

    <!-- 2. 카드 매출전표 팝업 (Rowspan 구조로 개선) -->
    <div v-if="showReceiptModal && activeItem" class="modal-overlay" @click="showReceiptModal = false">
      <div class="modal-content receipt-classic" @click.stop>
        <div class="classic-header">
          <h3>법인 신용카드 매출전표</h3>
          <button @click="showReceiptModal = false" class="classic-close">X</button>
        </div>
        <div class="classic-body">
          <!-- 상단 정보 -->
          <table class="classic-table">
            <colgroup><col width="20%"><col width="30%"><col width="20%"><col width="30%"></colgroup>
            <tbody>
              <tr>
                <th class="label-cell">카드종류</th>
                <td class="data-cell">{{ activeItem.KIND }}</td>
                <th class="label-cell">카드번호</th>
                <td class="data-cell">{{ activeItem.CARD_NUMC }}</td>
              </tr>
              <tr>
                <th class="label-cell">유효기간</th>
                <td class="data-cell">****</td>
                <th class="label-cell">구매자명</th>
                <td class="data-cell">{{ activeItem.NAME }}</td>
              </tr>
              <tr>
                <th class="label-cell">거래일시</th>
                <td class="data-cell">{{ formatFullDate(activeItem.APPR_DATE) }} {{ activeItem.APPR_TIME }}</td>
                <th class="label-cell">거래취소일</th>
                <td class="data-cell">-</td>
              </tr>
            </tbody>
          </table>

          <!-- 승인금액정보 (Rowspan 통합) -->
          <table class="classic-table section-table">
            <colgroup><col width="8%"><col width="27%"><col width="65%"></colgroup>
            <tbody>
              <tr>
                <th rowspan="5" class="section-label-cell"><span>승인금액정보</span></th>
                <th class="label-cell">승인번호</th>
                <td class="data-cell highlight-blue text-left">{{ activeItem.APPR_NUMC }}</td>
              </tr>
              <tr>
                <th class="label-cell">공급가액</th>
                <td class="data-cell highlight-red text-right">{{ formatAmount(activeItem.KRW_HWBAS) }}</td>
              </tr>
              <tr>
                <th class="label-cell">부가세</th>
                <td class="data-cell highlight-red text-right">{{ formatAmount(activeItem.KRW_HWSTE) }}</td>
              </tr>
              <tr>
                <th class="label-cell">봉사료</th>
                <td class="data-cell highlight-red text-right">0</td>
              </tr>
              <tr class="sum-row">
                <th class="label-cell">합계금액</th>
                <td class="data-cell highlight-red text-right font-bold">{{ formatAmount(activeItem.KRW_AMT) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- 공급자정보 (Rowspan 통합) -->
          <table class="classic-table section-table">
            <colgroup><col width="8%"><col width="22%"><col width="35%"><col width="15%"><col width="20%"></colgroup>
            <tbody>
              <tr>
                <th rowspan="3" class="section-label-cell"><span>공급자정보</span></th>
                <th class="label-cell">가맹점명</th>
                <td class="data-cell highlight-blue text-left">{{ activeItem.AFFI_NAME }}</td>
                <th class="label-cell">사업자번호</th>
                <td class="data-cell">2952900384</td>
              </tr>
              <tr>
                <th class="label-cell">대표자명</th>
                <td class="data-cell highlight-blue text-left">송*숙외3</td>
                <th class="label-cell">가맹점연락처</th>
                <td class="data-cell">-</td>
              </tr>
              <tr>
                <th class="label-cell">가맹점 주소</th>
                <td colspan="3" class="data-cell highlight-blue text-left">
                  경기 성남시 분당구 황새울로319번 6, 201호~207호 (서현동,텍스타워)
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 3. 전표 처리 상세 팝업 -->
    <div v-if="showProcessModal && activeItem" class="modal-overlay" @click="showProcessModal = false">
      <div class="modal-content process-detail-classic" @click.stop>
        <div class="classic-header">
          <h3>전표처리내역</h3>
          <button @click="showProcessModal = false" class="classic-close">X</button>
        </div>
        <div class="classic-body">
          <table class="vertical-table">
            <colgroup><col width="40%"><col width="60%"></colgroup>
            <tbody>
              <tr><th>전표번호</th><td>{{ activeItem.BELNR || '-' }}</td></tr>
              <tr><th>전기일자</th><td>{{ formatFullDate(activeItem.DOC_BUDAT) }}</td></tr>
              <tr><th>처리담당자</th><td>{{ activeItem.DOC_PERNAME || '-' }}</td></tr>
              <tr><th>처리일자</th><td>{{ formatFullDate(activeItem.DOC_BUDAT) }}</td></tr>
              <tr><th>처리상태</th><td>{{ activeItem.DOC_STATUS || '미처리' }}</td></tr>
              <tr><th>비용계정</th><td>부서운영비-중역실</td></tr>
              <tr><th>코스트센터</th><td>이태진</td></tr>
              <tr><th>부가세공제</th><td>불공제</td></tr>
              <tr><th>적요</th><td>{{ activeItem.DOC_SGTXT || '-' }}</td></tr>
            </tbody>
          </table>
          <div class="classic-footer">
            <button class="confirm-btn" @click="showProcessModal = false">확인</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. 비용처리 승인 팝업 -->
    <div v-if="showProcessConfirmModal" class="modal-overlay" @click="showProcessConfirmModal = false">
      <div class="modal-content confirm-modal" @click.stop>
        <div class="modal-header">
          <h3>비용 전송 확인</h3>
          <button @click="showProcessConfirmModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="worklistLoading" class="loading-inner">정보를 불러오는 중...</div>
          <div v-else>
            <div class="confirm-summary">
              선택 <strong>{{ selectedItems.length }}</strong>건 / 합계 <strong>{{ formatAmount(selectedTotalAmt) }}</strong>원
            </div>
            <div class="form-group">
              <label>전표 유형</label>
              <select v-model="selectedDocpr" class="f-input" @change="onDocprChange">
                <option value="">-- 전표 유형 선택 --</option>
                <option v-for="t in worklistTemplates" :key="t.DOCPR" :value="t.DOCPR">{{ t.DPTXT }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>적요</label>
              <select v-model="selectedSgtxt" class="f-input">
                <option value="">-- 적요 선택 --</option>
                <option v-for="s in filteredSgtxtList" :key="s.SGTXT" :value="s.SGTXT">{{ s.SGTXT }}</option>
              </select>
            </div>
            <button class="submit-btn" :disabled="!selectedDocpr || processingSubmit" @click="submitProcess">
              {{ processingSubmit ? '전송 중...' : 'ERP 전송 승인' }}
            </button>
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
const usages = ref([])
const loading = ref(true)
const selectedItems = ref([])
const showFilterModal = ref(false)
const showReceiptModal = ref(false)
const showProcessModal = ref(false)
const showProcessConfirmModal = ref(false)
const activeItem = ref(null)

const worklistLoading = ref(false)
const worklistTemplates = ref([])
const worklistDocprSgtxt = ref([])
const selectedDocpr = ref('')
const selectedSgtxt = ref('')
const processingSubmit = ref(false)

const filteredSgtxtList = computed(() => {
  if (!selectedDocpr.value) return []
  return worklistDocprSgtxt.value.filter(s => s.DOCPR === selectedDocpr.value)
})

const selectedTotalAmt = computed(() => {
  return selectedItems.value.reduce((acc, idx) => {
    const item = usages.value[idx]
    return acc + (Number(item?.KRW_AMT) || 0)
  }, 0)
})

const knownOwners = ref([])
const knownCards = ref([])

const updateKnownOptions = (data) => {
  data.forEach(item => {
    if (item.PERNR && !knownOwners.value.find(o => o.PERNR === item.PERNR)) {
      knownOwners.value.push({ PERNR: item.PERNR, NAME: item.NAME || item.PERNR })
    }
    if (item.CARD_NUMC && !knownCards.value.find(c => c.CARD_NUMC === item.CARD_NUMC)) {
      knownCards.value.push({ CARD_NUMC: item.CARD_NUMC, KIND: item.KIND })
    }
  })
}

const activePeriod = ref('')
const filterParams = ref({ cardOwner: '', cardNum: '', frDate: '', toDate: '', status: 'A' })

const setPeriod = (type) => {
  activePeriod.value = type
  const today = new Date()
  if (type === 'yesterday') {
    const y = new Date(today); y.setDate(y.getDate() - 1);
    filterParams.value.frDate = y.toISOString().slice(0, 10); filterParams.value.toDate = y.toISOString().slice(0, 10);
  } else if (type === '1week') {
    const p = new Date(today); p.setDate(today.getDate() - 7);
    filterParams.value.frDate = p.toISOString().slice(0, 10); filterParams.value.toDate = today.toISOString().slice(0, 10);
  } else if (type === 'thisMonth') {
    const f = new Date(today.getFullYear(), today.getMonth(), 1);
    filterParams.value.frDate = f.toISOString().slice(0, 10); filterParams.value.toDate = today.toISOString().slice(0, 10);
  } else if (type === 'lastMonth') {
    const f = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const l = new Date(today.getFullYear(), today.getMonth(), 0);
    filterParams.value.frDate = f.toISOString().slice(0, 10); filterParams.value.toDate = l.toISOString().slice(0, 10);
  }
}

const applyFilter = () => { showFilterModal.value = false; fetchUsages() }

const fetchUsages = async () => {
  loading.value = true; selectedItems.value = []
  try {
    const res = await axios.get('/api/v1/cards/usages', {
      params: {
        card_num: filterParams.value.cardNum || "",
        fr_date: filterParams.value.frDate ? filterParams.value.frDate.replace(/-/g, "") : "",
        to_date: filterParams.value.toDate ? filterParams.value.toDate.replace(/-/g, "") : "",
        pi_status: filterParams.value.status
      }
    })
    let rawData = res.data
    // 만약 리스트가 아니라 단일 객체로 왔을 경우 리스트로 변환
    if (rawData && !Array.isArray(rawData)) {
      rawData = [rawData]
    }
    usages.value = rawData || []
    updateKnownOptions(usages.value)
  } catch (err) { console.error(err) } finally { loading.value = false }
}

const formatFullDate = (val) => (val && val.length >= 8) ? `${val.substring(0,4)}-${val.substring(4,6)}-${val.substring(6,8)}` : '-'
const formatAmount = (val) => val ? new Intl.NumberFormat('ko-KR').format(val) : '0'

const getStatusClass = (s) => {
  if (!s || s === '미처리' || s === '비용 처리 전') return 's-ready'
  if (s.includes('진행') || s.includes('결재 중')) return 's-pending'
  if (s.includes('완료')) return 's-done'
  if (s.includes('반려') || s.includes('취소')) return 's-rejected'
  return 's-wait'
}

const toggleSelection = (idx) => {
  const currentIdx = selectedItems.value.indexOf(idx)
  if (currentIdx > -1) {
    selectedItems.value.splice(currentIdx, 1)
  } else {
    selectedItems.value.push(idx)
  }
}

const openReceiptModal = (item) => { activeItem.value = item; showReceiptModal.value = true }
const openProcessModal = (item) => { activeItem.value = item; showProcessModal.value = true }

const processExpenses = async () => {
  if (selectedItems.value.length === 0) return
  let bukrs = usages.value[selectedItems.value[0]].BUKRS
  showProcessConfirmModal.value = true; worklistLoading.value = true
  try {
    const res = await axios.get('/api/v1/cards/worklist', { params: { bukrs } })
    worklistTemplates.value = res.data.TE_TEMPLATE || []; worklistDocprSgtxt.value = res.data.TE_DOCPR_SGTXT || []
  } catch (err) { alert('템플릿 로드 실패') } finally { worklistLoading.value = false }
}

const onDocprChange = () => { selectedSgtxt.value = filteredSgtxtList.value[0]?.SGTXT || '' }

const submitProcess = async () => {
  if (!selectedDocpr.value) return
  if (!confirm('승인하시겠습니까?')) return
  processingSubmit.value = true
  try {
    const items = selectedItems.value.map(idx => {
      const i = usages.value[idx]
      return { BUKRS: i.BUKRS, APPR_DATE: i.APPR_DATE, CARD_NUMC: i.CARD_NUMC, APPR_NUMC: i.APPR_NUMC, DOCPR: selectedDocpr.value, PERNR: i.PERNR, SGTXT: selectedSgtxt.value }
    })
    await axios.post('/api/v1/cards/process', { items })
    alert('완료되었습니다.'); showProcessConfirmModal.value = false; fetchUsages()
  } catch (err) { alert('오류 발생') } finally { processingSubmit.value = false }
}

const cancelProcessing = async () => {
  if (selectedItems.value.length === 0) return
  if (!confirm('취소하시겠습니까?')) return
  try {
    const items = selectedItems.value.map(idx => {
      const i = usages.value[idx]
      return { BUKRS: i.BUKRS, BELNR: i.BELNR || '', GJAHR: i.GJAHR || '', CARD_NUMC: i.CARD_NUMC, APPR_DATE: i.APPR_DATE, APPR_NUMC: i.APPR_NUMC }
    })
    await axios.post('/api/v1/cards/cancel', { items })
    alert('취소 완료'); fetchUsages()
  } catch (err) { alert('취소 실패') }
}

onMounted(() => { setPeriod('thisMonth'); fetchUsages() })
</script>

<style scoped>
.usage-view { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 0 var(--space-lg) var(--space-lg); /* 상단 패딩 제거 */
}

/* --- View Header --- */
.view-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-end; 
  margin-bottom: var(--space-xl); 
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-subtle);
}

.header-left { 
  display: flex; 
  align-items: center; 
  gap: var(--space-md); 
}

.back-btn { 
  background: var(--bg-surface); 
  border: 1px solid var(--border-subtle); 
  width: 44px; 
  height: 44px; 
  border-radius: var(--radius-md); 
  cursor: pointer; 
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

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

.filter-trigger-btn { 
  padding: 0.75rem 1.5rem; 
  background: var(--bg-surface); 
  border: 1px solid var(--border-subtle); 
  border-radius: var(--radius-full); 
  font-weight: 600; 
  cursor: pointer; 
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.filter-trigger-btn:hover {
  border-color: var(--color-secondary);
  background: rgba(59, 130, 246, 0.1);
}

/* --- Layout & Fixed Areas --- */
.fixed-top-area {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-main);
  padding-top: var(--space-lg); /* 컨테이너에서 옮겨온 패딩 */
  padding-bottom: 4px;
}

/* --- View Header Styles (Synced with BudgetView) --- */
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

.filter-trigger-btn {
  height: 44px;
  padding: 0 20px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 14px;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-trigger-btn:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}

.action-bar-container { 
  margin-bottom: var(--space-xl); 
}

.action-bar { 
  background: rgba(30, 41, 59, 0.9); 
  backdrop-filter: blur(16px);
  color: white; 
  padding: 1.25rem 2rem; 
  border-radius: 8px; /* 8px로 통일 */
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  border: 1px solid var(--border-strong);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
}

.selection-status { font-size: 1rem; font-weight: 500; }
.selection-status strong { color: var(--color-primary); font-weight: 800; }
.placeholder { color: var(--text-dim); }

.btn-group { display: flex; gap: 12px; align-items: center; }

.action-btn { 
  padding: 0.75rem 1.75rem; 
  border-radius: 8px; /* 8px로 통일 */
  font-weight: 700; 
  border: none; 
  cursor: pointer; 
  font-size: 0.95rem;
  transition: all 0.2s;
}

.btn-primary { 
  background: #1e40af; 
  color: #ffffff; 
  border: 1px solid transparent; 
}
.btn-primary:hover { 
  background: #ffffff; /* 색상 반전 */
  color: #1e40af; 
  border-color: #1e40af;
}

.btn-outline { 
  background: #334155; 
  color: #ffffff; 
  border: 1px solid rgba(255,255,255,0.15); 
}
.btn-outline:hover { 
  background: #ffffff; /* 색상 반전 */
  color: #334155; 
  border-color: #334155;
}

.refresh-text-btn {
  background: #334155;
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.1);
  padding: 0.75rem 1.5rem;
  border-radius: 8px; /* 8px로 통일 */
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-text-btn:hover {
  background: #ffffff; /* 색상 반전 */
  color: #334155;
  border-color: #334155;
}

/* --- Usage Cards --- */
.usage-list { display: flex; flex-direction: column; gap: 1rem; }

.usage-card { 
  background: var(--bg-surface); 
  border: 1px solid var(--border-subtle); 
  border-radius: 8px; /* 8px로 통일 */
  padding: var(--space-md) var(--space-lg); 
  display: flex; 
  align-items: center; 
  gap: 24px; 
  transition: all 0.2s ease;
}

.usage-card:hover { 
  background: #243147;
  border-color: var(--border-strong); 
  transform: translateX(4px);
}

.usage-card.selected { 
  background: rgba(223, 255, 0, 0.05);
  border-color: var(--color-primary); 
}

.card-check { display: flex; align-items: center; }
.card-check input[type="checkbox"] {
  accent-color: var(--color-primary);
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.card-info { flex: 1; cursor: pointer; }
.top-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }

.merchant-name { 
  font-size: 1.2rem; 
  font-weight: 700; 
  color: #ffffff; 
}

.status-badge { 
  font-size: 0.7rem; 
  font-weight: 800; 
  padding: 4px 12px; 
  border-radius: var(--radius-full); 
  letter-spacing: 0.02em;
  transition: all 0.2s;
}

.status-badge.clickable {
  cursor: pointer;
}

.status-badge.clickable:hover {
  filter: brightness(1.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.s-ready { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); } /* 비용 처리 전 */
.s-pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); } /* 결재 중 */
.s-done { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); } /* 처리 완료 */
.s-rejected { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); } /* 반려/취소 */
.s-wait { background: #334155; color: #94a3b8; }

.bottom-row { 
  font-size: 0.9rem; 
  color: var(--text-dim); 
  display: flex;
  gap: 20px;
}

.card-price { 
  width: 220px; 
  text-align: right; 
  cursor: pointer; 
  border-left: 1px solid var(--border-subtle); 
  padding-left: var(--space-xl); 
}

.amount { 
  font-size: 1.6rem; 
  font-weight: 800; 
  color: #ffffff; 
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: -0.05em;
}

.user { font-size: 0.9rem; color: var(--text-muted); margin-top: 6px; font-weight: 600; }
.auth-no { font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }

/* --- Crystal Clarity Modals (Light Paper Theme) --- */
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

.modal-content { 
  background: #ffffff; /* White background for readability */
  border: 1px solid var(--border-strong);
  border-radius: 8px; /* 8px 통일 */
  overflow: hidden; 
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  max-width: 800px;
  width: 90%;
}

.receipt-classic { max-width: 700px; }

.classic-header { 
  background: #1e293b; 
  color: #ffffff; 
  padding: 24px 32px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  border-top-left-radius: 8px; /* 명시적 상단 곡률 추가 */
  border-top-right-radius: 8px; /* 명시적 상단 곡률 추가 */
}

.classic-header h3 { 
  margin: 0; 
  font-size: 1.25rem; 
  font-weight: 800; 
  letter-spacing: -0.01em;
}

.classic-close { 
  background: rgba(255,255,255,0.1); 
  border: none; 
  color: #ffffff; 
  width: 32px; height: 32px;
  border-radius: 8px; /* 8px 통일 */
  cursor: pointer; 
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}

.classic-close:hover {
  background: #ef4444;
}

.classic-body { padding: 32px; background: #ffffff; }

/* Table Stylings (High Contrast Light Mode) */
.classic-table, .vertical-table { 
  width: 100%; 
  border-collapse: separate; 
  border-spacing: 0;
  border: 1px solid #e2e8f0; 
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 24px;
}

.classic-table th, .classic-table td, .vertical-table th, .vertical-table td { 
  border-bottom: 1px solid #e2e8f0; 
  border-right: 1px solid #e2e8f0; 
  padding: 14px 16px; 
  font-size: 0.95rem; 
}

.classic-table th:last-child, .classic-table td:last-child { border-right: none; }
.classic-table tr:last-child td { border-bottom: none; }

.label-cell, .vertical-table th { 
  background: #f8fafc; 
  color: #475569; 
  font-weight: 700; 
  text-align: center;
}

.data-cell, .vertical-table td { 
  background: #ffffff; 
  color: #1e293b; 
  font-weight: 600;
}

.section-label-cell { 
  background: #f1f5f9; 
  border-right: 2px solid #e2e8f0 !important;
  vertical-align: middle;
  padding: 0 !important;
  width: 44px;
}

.section-label-cell span {
  transition: all 0.2s;
}

/* --- Filter Modal (GA Premium Redesign) --- */
.filter-modern {
  width: 520px;
  max-width: 95vw;
  background: #ffffff;
  border-radius: 8px; /* 8px로 통일 */
  overflow: hidden;
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.45);
}

.filter-body {
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.filter-group, .filter-section {
  display: flex;
  flex-direction: column;
}

.filter-group label, .filter-section label {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e293b; /* High Visibility Slate */
  margin-bottom: 10px;
  margin-left: 2px;
}

.modern-input {
  width: 100%;
  padding: 14px 18px;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px; /* 8px로 통일 */
  color: #1e293b;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

.modern-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.12), inset 0 2px 4px rgba(0, 0, 0, 0.02);
}

.period-btn-group, .status-btn-group {
  display: flex;
  background: #f1f5f9;
  padding: 6px;
  border-radius: 8px; /* 8px로 통일 */
  gap: 6px;
}

.period-btn, .status-tab-btn {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  border-radius: 8px; /* 8px로 통일 */
  transition: all 0.2s ease;
}

.period-btn:hover, .status-tab-btn:hover {
  color: #3b82f6;
  background: rgba(255, 255, 255, 0.6);
}

.period-btn.active, .status-tab-btn.active {
  background: #3b82f6; /* High Contrast Active */
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.date-range-box {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}

.range-sep {
  color: #94a3b8;
  font-weight: 800;
}

.filter-footer {
  padding: 24px 40px 40px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.apply-filter-btn {
  width: 100%;
  padding: 18px;
  background: #3b82f6;
  color: #ffffff;
  border: none;
  border-radius: 18px;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 12px 20px -5px rgba(59, 130, 246, 0.4);
  transition: all 0.3s;
}

.apply-filter-btn:hover {
  background: #2563eb;
  transform: translateY(-3px);
  box-shadow: 0 20px 30px -8px rgba(59, 130, 246, 0.5);
}

/* --- Receipt & Detail Modal (GA Final Optimized) --- */
.receipt-classic, .process-detail-classic { 
  width: 540px; /* Reduced Width for Mobile */
  max-width: 95vw; 
}

.classic-header {
  padding: 18px 24px;
  background: #1e3a8a; /* Consistent Blue */
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.classic-header h3 { font-size: 1.15rem; font-weight: 800; margin: 0; }
.classic-close { background: transparent; border: none; color: #cbd5e1; font-size: 1.4rem; cursor: pointer; transition: color 0.2s; }
.classic-close:hover { color: #ffffff; }

.classic-body { padding: 24px; background: #ffffff; }

/* Utility Classes */
.text-left { text-align: left !important; }
.text-right { text-align: right !important; }
.font-bold { font-weight: 800 !important; }

/* Highlight colors based on user attachment */
.highlight-blue { color: #2563eb !important; }
.highlight-red { color: #ef4444 !important; }

.receipt-table, .classic-table, .vertical-table {
  width: 100%; border-collapse: collapse; margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.receipt-table th, .receipt-table td, .classic-table th, .classic-table td, .vertical-table th, .vertical-table td {
  padding: 12px 14px; border: 1px solid #e2e8f0; font-size: 0.9rem;
}

.classic-table th, .vertical-table th, .label-cell { 
  background: #f8fafc; color: #475569; font-weight: 700; text-align: center; 
}
.data-cell, .vertical-table td { background: #ffffff; color: #1e293b; font-weight: 600; }

.sum-row th, .sum-row td { background: #fff1f2 !important; }
.sum-row td { font-weight: 800; font-size: 1.05rem; }

.classic-footer {
  padding-top: 10px;
  display: flex;
  justify-content: center;
}

.confirm-btn { 
  width: 100%; padding: 14px; 
  background: #1e40af; color: #ffffff; 
  border: none; border-radius: 12px; 
  font-size: 1rem; font-weight: 700; cursor: pointer; 
  transition: all 0.2s;
}

.confirm-btn:hover { background: #1e3a8a; transform: translateY(-1px); }

.loading-state { text-align: center; padding: 100px 0; color: #64748b; }
.spinner { 
  border: 3px solid #e2e8f0; 
  border-top: 3px solid #3b82f6; 
  border-radius: 50%; 
  width: 44px; height: 44px; 
  animation: spin 1s linear infinite; 
  margin: 0 auto 20px; 
}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Mobile Optimization */
@media (max-width: 768px) {
  .usage-card { flex-direction: column; align-items: flex-start; gap: 16px; }
  .card-price { width: 100%; border-left: none; border-top: 1px solid var(--border-subtle); padding: 16px 0 0; text-align: left; }
  .action-bar { padding: 12px 20px; flex-direction: column; gap: 16px; border-radius: var(--radius-lg); }
  .btn-group { width: 100%; justify-content: center; }
  .action-bar-container { top: 80px; }
}
</style>

