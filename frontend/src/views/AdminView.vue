<template>
  <div class="admin-view">
    <div class="fixed-top-area">
      <header class="admin-header">
        <div class="header-left">
          <button @click="router.push('/')" class="nav-icon-btn home" title="홈으로">
            <span class="icon">🏠</span>
          </button>
          <div class="title-group">
            <p class="admin-badge">SYSTEM ADMINISTRATION</p>
            <h1 class="admin-title">시스템 관리자 대시보드</h1>
          </div>
        </div>
        <div class="header-right">
          <button class="glass-btn refresh" @click="fetchUsers(); fetchContacts(); fetchNotices();" title="데이터 새로고침">
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

    <nav class="admin-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-item', { active: currentTab === tab.id }]"
        @click="currentTab = tab.id"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </nav>

    <div class="admin-content-area">
      <!-- 1. 사용자 권한 관리 -->
      <transition name="fade-slide" mode="out-in">
        <div v-if="currentTab === 'users'" :key="'users'" class="tab-panel">
          <div class="premium-card form-card">
            <div class="card-header">
              <h3>사용자 {{ userEditMode ? '정보 수정' : '신규 등록' }}</h3>
              <p class="card-desc">시스템 접근 권한을 가진 직원을 관리합니다.</p>
            </div>
            <form @submit.prevent="handleUserSubmit" class="modern-form">
              <div class="form-grid">
                <div class="form-group">
                  <label>사번</label>
                  <input v-model="userForm.emp_no" type="text" placeholder="예: BP26745" required :disabled="userEditMode" @input="userForm.emp_no = userForm.emp_no.toUpperCase()" />
                </div>
                <div class="form-group">
                  <label>성명</label>
                  <input v-model="userForm.kor_nm" type="text" placeholder="성명을 입력하세요" required />
                </div>
                <div class="form-group full-width">
                  <label>비밀번호</label>
                  <input v-model="userForm.password" type="password" :placeholder="userEditMode ? '변경 시에만 입력하십시오' : '초기 비밀번호를 설정하십시오'" :required="!userEditMode" />
                </div>
              </div>
              <div class="form-options">
                <label class="premium-checkbox">
                  <input v-model="userForm.is_admin" type="checkbox" />
                  <span class="check-mark"></span>
                  관리자(Admin) 권한 부여
                </label>
              </div>
              <div class="form-actions">
                <button type="submit" class="btn-primary">{{ userEditMode ? '수정 완료' : '사용자 추가' }}</button>
                <button v-if="userEditMode" type="button" @click="resetUserForm" class="btn-ghost">취소</button>
              </div>
            </form>
          </div>

          <div class="premium-card list-card">
            <div class="card-header">
              <h3>사용자 목록</h3>
              <div class="search-box">
                <input type="text" placeholder="이름 또는 사번 검색..." class="small-input" />
              </div>
            </div>
            <div class="data-list">
              <div v-for="u in users" :key="u.EMP_NO" class="list-row">
                <div class="row-main">
                  <div class="user-avatar">{{ u.KOR_NM.charAt(0) }}</div>
                  <div class="user-info">
                    <span class="u-id">{{ u.EMP_NO }}</span>
                    <span class="u-name">{{ u.KOR_NM }}</span>
                    <span v-if="u.IS_ADMIN" class="status-badge admin">ADMIN</span>
                  </div>
                </div>
                <div class="row-actions">
                  <button @click="editUser(u)" class="icon-btn edit">✎</button>
                  <button @click="deleteUser(u.EMP_NO)" class="icon-btn delete" :disabled="u.EMP_NO === loginEmpNo">🗑</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. 공지사항 관리 -->
        <div v-else-if="currentTab === 'notices'" :key="'notices'" class="tab-panel">
          <div class="premium-card form-card">
            <div class="card-header">
              <h3>공지사항 {{ noticeEditMode ? '수정' : '작성' }}</h3>
            </div>
            <form @submit.prevent="handleNoticeSubmit" class="modern-form">
              <div class="form-group">
                <label>공지 제목</label>
                <input v-model="noticeForm.subject" type="text" placeholder="공지 제목을 입력하세요" required />
              </div>
              <div class="form-group">
                <label>공지 내용</label>
                <textarea v-model="noticeForm.content" placeholder="공지 내용을 상세히 작성하세요" required rows="6"></textarea>
              </div>
              <div class="form-actions">
                <button type="submit" class="btn-primary">{{ noticeEditMode ? '공지 수정' : '공지 게시' }}</button>
                <button v-if="noticeEditMode" type="button" @click="resetNoticeForm" class="btn-ghost">취소</button>
              </div>
            </form>
          </div>

          <div class="premium-card list-card">
            <h3>등록된 공지사항</h3>
            <div class="data-list">
              <div v-for="n in notices" :key="n.ID" class="list-row">
                <div class="row-main">
                  <div class="info-content">
                    <span class="item-title">{{ n.SUBJECT }}</span>
                    <span class="item-meta">{{ formatDate(n.ERDAT) }} | 작성자: {{ n.ERNAM }}</span>
                  </div>
                </div>
                <div class="row-actions">
                  <button @click="editNotice(n)" class="icon-btn edit">✎</button>
                  <button @click="deleteNotice(n.ID)" class="icon-btn delete">🗑</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. 연락처 관리 -->
        <div v-else-if="currentTab === 'contacts'" :key="'contacts'" class="tab-panel">
          <div class="premium-card form-card">
            <div class="card-header">
              <h3>담당자 연락처 {{ contactEditMode ? '수정' : '등록' }}</h3>
            </div>
            <form @submit.prevent="handleContactSubmit" class="modern-form">
              <div class="form-grid">
                <div class="form-group"><label>부서/구분</label><input v-model="contactForm.division" type="text" placeholder="예: 경영지원팀" required /></div>
                <div class="form-group"><label>성명</label><input v-model="contactForm.name" type="text" placeholder="성명" required /></div>
                <div class="form-group"><label>직급</label><input v-model="contactForm.title" type="text" placeholder="직급" /></div>
                <div class="form-group"><label>연락처</label><input v-model="contactForm.tel" type="text" placeholder="010-0000-0000" required /></div>
                <div class="form-group full-width"><label>업무 내용</label><input v-model="contactForm.task" type="text" placeholder="담당 업무 상세" /></div>
              </div>
              <div class="form-actions">
                <button type="submit" class="btn-primary highlight">{{ contactEditMode ? '연락처 수정' : '연락처 등록' }}</button>
                <button v-if="contactEditMode" type="button" @click="resetContactForm" class="btn-ghost">취소</button>
              </div>
            </form>
          </div>

          <div class="premium-card list-card">
            <h3>내부 연락처 목록</h3>
            <div class="data-list">
              <div v-for="c in contacts" :key="c.ID" class="list-row">
                <div class="row-main">
                  <div class="info-content">
                    <span class="item-title">{{ c.DIVISION }} {{ c.NAME }} <small>{{ c.TITLE }}</small></span>
                    <span class="item-meta">{{ c.TEL }} | {{ c.TASK || '업무 미지정' }}</span>
                  </div>
                </div>
                <div class="row-actions">
                  <button @click="editContact(c)" class="icon-btn edit">✎</button>
                  <button @click="deleteContact(c.ID)" class="icon-btn delete">🗑</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <div v-if="message" :class="['status-toast', { error: isError }]">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const currentTab = ref('users')
const message = ref('')
const isError = ref(false)

const users = ref([])
const contacts = ref([])
const notices = ref([])
const loginEmpNo = ref(localStorage.getItem('kor_nm'))

const tabs = [
  { id: 'users', label: '권한 관리', icon: '👥' },
  { id: 'notices', label: '공지 관리', icon: '🔔' },
  { id: 'contacts', label: '연락처 관리', icon: '📞' }
]

const userEditMode = ref(false)
const userForm = ref({ emp_no: '', kor_nm: '', password: '', is_admin: false })
const noticeEditMode = ref(false)
const noticeForm = ref({ id: null, subject: '', content: '' })
const contactEditMode = ref(false)
const contactForm = ref({ id: null, division: '', title: '', name: '', tel: '', email: '', task: '', remark: '' })

const fetchUsers = async () => { try { const res = await axios.get('/api/v1/admin/users'); users.value = res.data; } catch (err) { } }
const fetchContacts = async () => { try { const res = await axios.get('/api/v1/admin/contacts'); contacts.value = res.data; } catch (err) { } }
const fetchNotices = async () => { try { const res = await axios.get('/api/v1/admin/notices'); notices.value = res.data; } catch (err) { } }

const handleUserSubmit = async () => {
  try {
    if (userEditMode.value) {
      await axios.put(`/api/v1/admin/users/${userForm.value.emp_no}`, { kor_nm: userForm.value.kor_nm, password: userForm.value.password || undefined, is_admin: userForm.value.is_admin })
      showMsg('사용자 정보가 수정되었습니다.')
    } else {
      await axios.post('/api/v1/admin/users', userForm.value)
      showMsg('사용자가 등록되었습니다.')
    }
    resetUserForm(); fetchUsers()
  } catch (err) { showMsg('오류: ' + (err.response?.data?.detail || '저장 실패'), true) }
}

const handleNoticeSubmit = async () => {
  try {
    if (noticeEditMode.value) { await axios.put(`/api/v1/admin/notices/${noticeForm.value.id}`, noticeForm.value); showMsg('공지사항이 수정되었습니다.') }
    else { await axios.post('/api/v1/admin/notices', noticeForm.value); showMsg('공지사항이 게시되었습니다.') }
    resetNoticeForm(); fetchNotices()
  } catch (err) { showMsg('공지 저장 실패', true) }
}

const handleContactSubmit = async () => {
  try {
    if (contactEditMode.value) { await axios.put(`/api/v1/admin/contacts/${contactForm.value.id}`, contactForm.value); showMsg('연락처가 수정되었습니다.') }
    else { await axios.post('/api/v1/admin/contacts', contactForm.value); showMsg('연락처가 등록되었습니다.') }
    resetContactForm(); fetchContacts()
  } catch (err) { showMsg('연락처 저장 실패', true) }
}

const deleteUser = async (id) => { if (confirm('삭제하시겠습니까?')) { try { await axios.delete(`/api/v1/admin/users/${id}`); fetchUsers(); showMsg('삭제 완료') } catch (err) { showMsg('삭제 실패', true) } } }
const deleteNotice = async (id) => { if (confirm('삭제하시겠습니까?')) { try { await axios.delete(`/api/v1/admin/notices/${id}`); fetchNotices(); showMsg('삭제 완료') } catch (err) { showMsg('삭제 실패', true) } } }
const deleteContact = async (id) => { if (confirm('삭제하시겠습니까?')) { try { await axios.delete(`/api/v1/admin/contacts/${id}`); fetchContacts(); showMsg('삭제 완료') } catch (err) { showMsg('삭제 실패', true) } } }

const editUser = (u) => { userEditMode.value = true; userForm.value = { emp_no: u.EMP_NO, kor_nm: u.KOR_NM, password: '', is_admin: !!u.IS_ADMIN }; window.scrollTo(0,0) }
const editNotice = (n) => { noticeEditMode.value = true; noticeForm.value = { id: n.ID, subject: n.SUBJECT, content: n.CONTENT }; window.scrollTo(0,0) }
const editContact = (c) => { 
  contactEditMode.value = true; 
  contactForm.value = { 
    id: c.ID, 
    division: c.DIVISION, 
    title: c.TITLE, 
    name: c.NAME, 
    tel: c.TEL, 
    email: c.EMAIL || '', 
    task: c.TASK, 
    remark: c.REMARK || '' 
  }; 
  window.scrollTo(0,0) 
}

const resetUserForm = () => { userForm.value = { emp_no: '', kor_nm: '', password: '', is_admin: false }; userEditMode.value = false }
const resetNoticeForm = () => { noticeForm.value = { id: null, subject: '', content: '' }; noticeEditMode.value = false }
const resetContactForm = () => { contactForm.value = { id: null, division: '', title: '', name: '', tel: '', email: '', task: '', remark: '' }; contactEditMode.value = false }

const showMsg = (txt, error = false) => { message.value = txt; isError.value = error; setTimeout(() => message.value = '', 3000) }
const formatDate = (d) => { if (!d) return ''; if (d.length === 8) return `${d.substr(0,4)}.${d.substr(4,2)}.${d.substr(6,2)}`; return new Date(d).toLocaleDateString() }

watch(currentTab, () => message.value = '')
onMounted(() => { if (localStorage.getItem('is_admin') !== 'true') { router.replace('/') } else { fetchUsers(); fetchContacts(); fetchNotices() } })
</script>

<style scoped>
.admin-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg) var(--space-lg); /* 상단 패딩 제거 */
}

/* --- Header Section --- */
.admin-header {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-subtle);
}

.back-btn {
  background: var(--bg-surface); 
  border: 1px solid var(--border-subtle); 
  width: 44px; height: 44px;
  border-radius: 8px; /* 8px 통일 */
  cursor: pointer; 
  display: flex; align-items: center; justify-content: center;
  color: #ffffff; transition: all 0.2s;
}

.back-btn:hover { 
  background: var(--color-primary-soft); 
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.admin-badge { 
  font-size: 0.75rem; 
  font-weight: 800; 
  color: var(--color-secondary); 
  letter-spacing: 0.1em; 
  margin-bottom: 4px; 
}

.admin-title { 
  font-size: 1.75rem; 
  font-weight: 800; 
  color: #ffffff; 
  margin: 0; 
  letter-spacing: -0.02em;
}

/* --- Tabs --- */
.admin-tabs {
  display: flex; 
  gap: 8px; 
  margin-bottom: var(--space-xl);
  background: var(--bg-surface); 
  padding: 6px; 
  border-radius: 8px; /* 8px 통일 */
  border: 1px solid var(--border-subtle);
}

.tab-item {
  flex: 1; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  gap: 10px;
  padding: 12px; 
  border: none; 
  background: none; 
  cursor: pointer;
  border-radius: 8px; /* 8px 통일 */
  font-weight: 700; 
  color: var(--text-dim); 
  transition: all 0.2s ease;
}

.tab-item.active { 
  background: var(--color-secondary); 
  color: #ffffff; 
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); 
}

.tab-item:not(.active):hover {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

/* --- Form Design --- */
.form-card { 
  margin-bottom: var(--space-xl); 
  border-top: 3px solid var(--color-secondary); 
}

.card-header { margin-bottom: var(--space-lg); }
.card-header h3 { font-size: 1.3rem; font-weight: 800; color: #ffffff; margin-bottom: 6px; }
.card-desc { font-size: 0.85rem; color: var(--text-dim); font-weight: 500; }

.modern-form { display: flex; flex-direction: column; gap: 24px; }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.full-width { grid-column: span 2; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { 
  font-size: 0.8rem; 
  font-weight: 700; 
  color: var(--text-muted); 
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-group input, .form-group textarea {
  padding: 14px; 
  border: 1px solid var(--border-subtle); 
  border-radius: 8px; /* 8px 통일 */
  background: var(--bg-main); 
  color: #ffffff;
  font-size: 1rem; 
  transition: all 0.2s;
}

.form-group input:focus, .form-group textarea:focus { 
  border-color: var(--color-secondary); 
  outline: none; 
  background: #1e293b; 
}

.form-options { margin: 10px 0; }
.premium-checkbox { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  cursor: pointer; 
  font-size: 0.9rem; 
  font-weight: 600; 
  color: var(--text-main);
}

.premium-checkbox input { 
  width: 18px; 
  height: 18px; 
  accent-color: var(--color-secondary);
}

.form-actions { display: flex; gap: 12px; margin-top: 12px; }

.btn-primary {
  flex: 2; 
  padding: 14px; 
  border-radius: 8px; /* 8px 통일 */
  border: 1px solid transparent; 
  font-weight: 800;
  background: var(--color-secondary); 
  color: #ffffff; 
  cursor: pointer; 
  transition: all 0.2s;
}

.btn-primary:hover { 
  background: #ffffff; /* 색상 반전 */
  color: var(--color-secondary);
  border-color: var(--color-secondary);
  transform: translateY(-2px); 
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-ghost {
  flex: 1; 
  padding: 14px; 
  border-radius: 8px; /* 8px 통일 */
  border: 1px solid var(--border-subtle);
  background: transparent; 
  color: var(--text-dim); 
  font-weight: 700; 
  cursor: pointer;
  transition: all 0.2s;
}

.btn-ghost:hover {
  background: #ffffff; /* 색상 반전 */
  color: var(--bg-main);
  border-color: #ffffff;
}

/* --- List Design --- */
.list-card {
  background: var(--bg-surface);
}

.list-card h3 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: var(--space-lg);
}

.data-list { display: flex; flex-direction: column; }

.list-row {
  display: flex; 
  justify-content: space-between; 
  align-items: center;
  padding: 18px 0; 
  border-bottom: 1px solid var(--border-subtle);
}

.list-row:last-child { border-bottom: none; }

.row-main { display: flex; align-items: center; gap: 16px; }

.user-avatar {
  width: 44px; height: 44px; 
  border-radius: var(--radius-md); 
  background: var(--bg-main);
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; color: var(--color-secondary);
  border: 1px solid var(--border-strong);
}

.user-info { display: flex; align-items: center; gap: 10px; }
.u-id { 
  font-family: 'JetBrains Mono', monospace; 
  font-weight: 700; 
  color: var(--color-secondary); 
  font-size: 0.9rem;
}
.u-name { font-weight: 700; color: #ffffff; }

.status-badge { 
  font-size: 0.65rem; 
  font-weight: 900; 
  padding: 2px 8px; 
  border-radius: var(--radius-full); 
  text-transform: uppercase;
}
.status-badge.admin { 
  background: rgba(59, 130, 246, 0.1); 
  color: var(--color-secondary); 
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.info-content { display: flex; flex-direction: column; gap: 6px; }
.item-title { font-weight: 700; color: #ffffff; font-size: 1.05rem; }
.item-title small { color: var(--text-muted); font-weight: 500; font-size: 0.85rem; }
.item-meta { 
  font-size: 0.85rem; 
  color: var(--text-dim); 
  font-family: 'JetBrains Mono', monospace;
}

.row-actions { display: flex; gap: 10px; }

.icon-btn {
  width: 36px; height: 36px; 
  border-radius: var(--radius-md); 
  border: 1px solid var(--border-subtle); 
  cursor: pointer;
  display: flex; align-items: center; justify-content: center; 
  font-size: 1rem;
  background: var(--bg-main);
  color: var(--text-dim);
  transition: all 0.2s;
}

.icon-btn.edit:hover { 
  background: rgba(59, 130, 246, 0.1); 
  color: var(--color-secondary); 
  border-color: var(--color-secondary);
}

.icon-btn.delete:hover { 
  background: rgba(239, 68, 68, 0.1); 
  color: var(--color-danger); 
  border-color: var(--color-danger);
}

.icon-btn.delete:disabled { opacity: 0.2; cursor: not-allowed; }

/* --- Status Toast --- */
.status-toast {
  position: fixed; 
  bottom: 40px; 
  left: 50%; 
  transform: translateX(-50%);
  background: var(--bg-surface); 
  color: #ffffff; 
  padding: 14px 28px;
  border-radius: var(--radius-md); 
  font-weight: 800; 
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-secondary);
  z-index: 2000; 
  animation: bounceUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.status-toast.error { 
  color: var(--color-danger); 
  border-color: var(--color-danger); 
}

@keyframes bounceUp { 
  from { bottom: -60px; opacity: 0; } 
  to { bottom: 40px; opacity: 1; } 
}

@keyframes fadeSlide { 
  from { opacity: 0; transform: translateY(15px); } 
  to { opacity: 1; transform: translateY(0); } 
}

.fade-slide-enter-active { animation: fadeSlide 0.4s ease; }

/* --- Admin Header (Fixed Area) --- */
.fixed-top-area {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-main);
  padding-top: var(--space-lg); /* 컨테이너 패딩 이전 */
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-subtle);
  height: 90px; /* 패딩 포함 높이 조정 */
  display: flex;
  align-items: center;
}

/* --- View Header Styles (Synced) --- */
.admin-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 0 var(--space-xl);
  width: 100%;
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

.glass-btn.refresh .icon {
  display: inline-block;
  color: #fbbf24; /* Warning/Admin color */
}

.glass-btn.refresh:active .icon {
  animation: rotate 0.5s linear;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.admin-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
}


@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .full-width { grid-column: auto; }
  .admin-tabs { border-radius: var(--radius-lg); }
}
</style>
