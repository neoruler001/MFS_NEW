<template>
  <div class="notice-view">
    <div class="fixed-top-area">
      <header class="view-header">
        <div class="header-left">
          <button @click="router.push('/')" class="nav-icon-btn home" title="홈으로">
            <span class="icon">🏠</span>
          </button>
          <div class="title-group">
            <p class="view-badge">CORPORATE ANNOUNCEMENTS</p>
            <h2 class="view-title">공지사항 및 안내</h2>
          </div>
        </div>
        <div class="header-right">
          <button class="glass-btn refresh" @click="fetchNotices" :class="{ spinning: loading }">
            <span class="icon">↻</span>
            <span class="label">새로고침</span>
          </button>
          <button @click="router.back()" class="glass-btn back" title="뒤로가기">
            <span class="icon">←</span>
            <span class="label">뒤로가기</span>
          </button>
        </div>
      </header>
      <div class="search-bar">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchKeyword"
          type="text"
          class="search-input"
          placeholder="제목 키워드로 검색..."
        />
        <button
          v-if="searchKeyword"
          class="search-clear-btn"
          @click="searchKeyword = ''"
          title="검색어 지우기"
        >✕</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="modern-loader"></div>
      <p>중요 공지를 동기화 중입니다...</p>
    </div>
    
    <div v-else class="notice-container">
      <div 
        v-for="(item, idx) in filteredNotices" 
        :key="idx" 
        class="premium-card notice-executive-card"
        :class="{ 'is-expanded': expandedId === idx }"
      >
        <div class="card-header" @click="toggleNotice(idx)">
          <div class="notice-info-group">
            <div class="notice-index">{{ String(idx + 1).padStart(2, '0') }}</div>
            <div class="notice-main">
              <div class="notice-meta-tags">
                <span class="tag-badge critical">IMPORTANT</span>
                <span class="tag-date">{{ formatDate(item.ERDAT) }}</span>
              </div>
              <h3 class="notice-subject">{{ item.SUBJECT }}</h3>
            </div>
          </div>
          <div class="chevron-box">
            <svg class="chevron-svg" viewBox="0 0 24 24">
              <path fill="currentColor" d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
            </svg>
          </div>
        </div>
        
        <transition name="expand">
          <div class="card-body" v-if="expandedId === idx">
            <div class="document-container">
              <div class="doc-header">
                <div class="doc-logo">HD HYUNDAI</div>
                <div class="doc-meta">
                  <span>작성자: {{ item.ERNAM || '시스템 관리자' }}</span>
                  <span>일자: {{ formatDate(item.ERDAT) }}</span>
                </div>
              </div>
              <div 
                class="doc-content rendered-html" 
                v-html="DOMPurify.sanitize(formatContent(item.CONTENTS), { ADD_ATTR: ['data-url', 'data-filename'] })"
                @click.prevent="handleContentClick"
              ></div>
              <div class="doc-footer">본 공지는 사내 보안 규정을 준수합니다.</div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DOMPurify from 'dompurify'

const router = useRouter()
const notices = ref([])
const loading = ref(true)
const expandedId = ref(0)
const searchKeyword = ref('')

const filteredNotices = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase();
  return notices.value.filter(item => {
    if (!item.SUBJECT || item.SUBJECT.trim().length === 0) return false;
    if (!keyword) return true;
    return item.SUBJECT.toLowerCase().includes(keyword);
  });
})

const fetchNotices = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/notices/notices')
    notices.value = res.data || []
  } catch (err) { console.error(err) } finally { loading.value = false }
}

// ✅ 이벤트 위임 방식: DOMPurify onclick 차단 문제 해결
const handleContentClick = (event) => {
  const link = event.target.closest('.doc-link-executive');
  if (!link) return;
  
  event.preventDefault();
  event.stopPropagation();
  
  const url = link.dataset.url;
  const fileName = link.dataset.filename;
  
  if (!url) return;
  
  // 현재 페이지를 유지하면서 파일만 다운로드
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.target = '_blank';   // CORS 에러 없이 새 탭에서 파일을 처리
  document.body.appendChild(a);
  a.click();
  setTimeout(() => document.body.removeChild(a), 200);
};

// -------------------------------------------------------
// ✅ 핵심 수정: filePath= 파라미터에서 실제 URL 추출
// 원본 데이터 예시:
//   touch1_imagestreaming_http.pdf&type=jpg&dpi=96&filePath=https://fcmerp.hhi.co.kr/Pds/파일명.pdf
// 실제 다운로드 URL: filePath= 뒤의 https:// 경로
// -------------------------------------------------------
const extractRealUrl = (rawUrl) => {
  // filePath= 파라미터가 있으면 그 값을 실제 URL로 사용
  const filePathMatch = rawUrl.match(/filePath=(https?:\/\/[^\s"&]+)/i);
  if (filePathMatch) {
    return decodeURIComponent(filePathMatch[1]);
  }
  // filePath가 없으면 원본 URL 그대로 사용
  return rawUrl;
};

const formatContent = (content) => {
  if (!content) return ''
  
  // 1. 구분자 처리
  let lines = content.split(/[|\n]/);
  let html = '';
  
  lines.forEach(line => {
    if (!line.trim()) return;
    
    // PDF 파일이나 http 링크가 포함된 줄인 경우
    if (line.includes('.pdf') || line.includes('http')) {
      // 전체 매칭 패턴: http로 시작하거나 .pdf를 포함하는 연속된 비공백 문자열
      const urlMatch = line.match(/(https?:\/\/[^\s"]+|[^\s"]+\.pdf[^\s"]*)/);
      if (urlMatch) {
        const rawUrl = urlMatch[0];
        
        // ✅ filePath= 파라미터에서 실제 파일 URL 추출
        const realUrl = extractRealUrl(rawUrl);
        const fileName = realUrl.split('/').pop().split('?')[0];
        
        // 설명 텍스트: "(PDF)모바일/웹 재무시스템 사용자매뉴얼" 같은 흰색 글자
        const descText = line
          .replace(rawUrl, '')
          .replace(/["'>]/g, '')
          .replace(/^\s*\(PDF\)\s*/i, '')
          .trim();
        
        html += `<div class="doc-link-container">
                  <a class="doc-link-executive"
                     data-url="${realUrl}"
                     data-filename="${fileName}">
                    <span class="icon">📄</span>
                    <span class="url-text">${fileName}</span>
                    <span class="desc-text">${descText || '(PDF) 다운로드'}</span>
                  </a>
                </div>`;
      } else {
        html += `<p class="normal-text">${line}</p>`;
      }
    } else {
      html += `<p class="normal-text">${line}</p>`;
    }
  });
  
  return html;
}

const formatDate = (dateStr) => {
  if (!dateStr || dateStr.length < 8) return ''
  return `${dateStr.substr(0,4)}.${dateStr.substr(4,2)}.${dateStr.substr(6,2)}`
}

const toggleNotice = (id) => {
  expandedId.value = expandedId.value === id ? null : id
}

onMounted(fetchNotices)
</script>

<style scoped>
.notice-view { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 0 var(--space-lg) var(--space-lg); /* 상단 패딩 제거 */
}

/* --- Fixed Top Area --- */
.fixed-top-area {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-main);
  padding-top: var(--space-lg); /* 컨테이너 패딩 이전 */
  padding-bottom: 2px;
}

.view-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: var(--space-lg);
  padding: var(--space-md) var(--space-lg) 0;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.view-badge { 
  font-size: 0.75rem; 
  font-weight: 800; 
  color: var(--color-secondary); 
  letter-spacing: 0.05em; 
  margin-bottom: 4px; 
}

.view-title { 
  font-size: 1.75rem; 
  font-weight: 800; 
  color: #ffffff; 
  margin: 0; 
  letter-spacing: -0.02em;
}

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
  color: #3b82f6;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* --- Search Bar --- */
.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 var(--space-lg);
  margin-bottom: var(--space-md);
  position: relative;
}

.search-icon {
  position: absolute;
  left: calc(var(--space-lg) + 14px);
  font-size: 1rem;
  pointer-events: none;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 12px 20px 12px 40px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 600;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-input::placeholder {
  color: var(--text-muted);
  font-weight: 500;
}

.search-input:focus {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.08);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-clear-btn {
  position: absolute;
  right: calc(var(--space-lg) + 12px);
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: var(--text-dim);
  font-size: 0.85rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.search-clear-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* --- Notice Container & Cards --- */
.notice-container { 
  display: flex; 
  flex-direction: column; 
  gap: 1rem; 
}

.notice-executive-card {
  padding: 0; 
  border: 1px solid var(--border-subtle); 
  border-radius: 8px; /* 8px 통일 */
  background: var(--bg-surface);
  transition: all 0.3s ease; 
  overflow: hidden;
}

.notice-executive-card:hover { 
  border-color: var(--color-secondary); 
  background: #243147;
}

.notice-executive-card.is-expanded { 
  border-color: var(--color-secondary); 
  background: #1e293b; 
}

.card-header { 
  padding: 24px var(--space-xl); 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  cursor: pointer; 
}

.notice-info-group { 
  display: flex; 
  align-items: center; 
  gap: 24px; 
}

.notice-index { 
  font-size: 1.25rem; 
  font-weight: 900; 
  color: var(--border-strong); 
  font-family: 'JetBrains Mono', monospace;
}

.is-expanded .notice-index {
  color: var(--color-secondary);
}

.notice-meta-tags { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  margin-bottom: 8px; 
}

.tag-badge { 
  font-size: 0.7rem; 
  font-weight: 900; 
  padding: 2px 10px; 
  border-radius: var(--radius-md); 
}

.tag-badge.critical { 
  background: rgba(59, 130, 246, 0.1); 
  color: var(--color-secondary); 
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.tag-date { 
  font-size: 0.85rem; 
  color: var(--text-dim); 
  font-weight: 600; 
  font-family: 'JetBrains Mono', monospace;
}

.notice-subject { 
  font-size: 1.2rem; 
  font-weight: 800; 
  color: #ffffff; 
  margin: 0; 
  line-height: 1.4; 
  transition: color 0.3s; 
}

.is-expanded .notice-subject { 
  color: var(--color-secondary); 
}

.chevron-box { 
  width: 36px; height: 36px; 
  border-radius: var(--radius-md); 
  background: var(--bg-main); 
  display: flex; align-items: center; justify-content: center; 
  color: var(--text-dim); 
  transition: all 0.3s; 
  border: 1px solid var(--border-subtle);
}

.is-expanded .chevron-box { 
  transform: rotate(180deg); 
  background: var(--color-secondary); 
  color: #ffffff; 
  border-color: var(--color-secondary);
}

/* --- Document Content --- */
.card-body { padding: 0 var(--space-xl) var(--space-xl); }

.document-container {
  background: var(--bg-main); 
  border-radius: var(--radius-md); 
  padding: var(--space-xl); 
  border: 1px solid var(--border-strong);
  position: relative; 
}

.document-container::before { 
  content: ""; 
  position: absolute; 
  top: 0; left: 0; width: 100%; height: 3px; 
  background: var(--color-secondary); 
}

.doc-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 24px; 
  padding-bottom: 16px; 
  border-bottom: 1px dashed var(--border-subtle); 
}

.doc-logo { 
  font-weight: 900; 
  color: var(--text-dim); 
  letter-spacing: 4px; 
  font-size: 0.75rem; 
}

.doc-meta { 
  font-size: 0.85rem; 
  color: var(--text-muted); 
  font-weight: 700; 
  display: flex; gap: 16px; 
}

.doc-content { 
  font-size: 1.05rem; 
  line-height: 1.8; 
  color: var(--text-main); 
  font-weight: 500; 
}

.doc-content :deep(.doc-link-container) {
  margin: 12px 0;
}

.doc-content :deep(.doc-link-executive) {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 20px;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
  cursor: pointer; /* ✅ 손모양 커서 강제 적용 */
}

.doc-content :deep(.doc-link-executive:hover) {
  background: rgba(59, 130, 246, 0.12);
  border-color: #3b82f6;
  transform: translateX(8px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2), 0 0 15px rgba(59, 130, 246, 0.1);
}

.doc-content :deep(.doc-link-executive .icon) {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.doc-content :deep(.url-text) {
  color: #3b82f6;
  font-size: 0.9rem;
  font-weight: 500;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding-right: 12px;
  margin-right: 4px;
}

.doc-content :deep(.desc-text) {
  color: #ffffff;
  font-weight: 700;
  font-size: 1rem;
}

.doc-content :deep(.normal-text) {
  margin-bottom: 8px;
}

.doc-footer { 
  margin-top: 30px; 
  padding-top: 16px; 
  border-top: 1px solid var(--border-subtle); 
  text-align: center; 
  font-size: 0.75rem; 
  color: var(--text-muted); 
  font-weight: 800; 
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Transitions */
.expand-enter-active, .expand-leave-active { transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); max-height: 2000px; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }

.loading-state { text-align: center; padding: 100px 0; color: var(--text-dim); }
.modern-loader { 
  width: 44px; height: 44px; 
  border: 3px solid var(--border-subtle); 
  border-top-color: var(--color-secondary); 
  border-radius: 50%; 
  animation: spin 1s linear infinite; 
  margin: 0 auto 20px; 
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
