# Vue Pattern — MFS Vue 3 컴포넌트 + API 호출 컨벤션

추출 시각: 2026-06-11
샘플 파일 수: 6 (main.js, router/index.js, LoginView.vue, CardUsageView.vue, AdminView.vue, App.vue)
신뢰도: HIGH (전체 컴포넌트 Composition API 통일)

---

## 올바른 패턴

### 1. Composition API — `<script setup>` 구조 (빈도: 100%)

모든 컴포넌트가 `<script setup>` 방식의 Composition API를 사용한다.  
Options API 미사용.

```vue
<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 상태 선언 — ref() 직접 사용 (Pinia store 미사용)
const loading = ref(false)
const error = ref('')
const users = ref([])
const currentTab = ref('users')

// 폼 상태 — ref()로 객체 관리
const userForm = ref({ emp_no: '', kor_nm: '', password: '', is_admin: false })

// onMounted: 초기 데이터 로딩
onMounted(() => {
  fetchUsers()
})
</script>
```

---

### 2. axios API 호출 패턴 (빈도: 100%)

컴포넌트별 `axios` 직접 import 사용. 중앙 서비스 레이어 없음.  
모든 호출은 `async/await + try/catch` 패턴.

```javascript
// 조회 패턴 (AdminView.vue:220)
const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/v1/admin/users')
    users.value = res.data
  } catch (err) {
    // 묵시적 무시 또는 에러 메시지 표시
  }
}

// 변경 패턴 — 성공 메시지 + 목록 갱신 (AdminView.vue:224-234)
const handleUserSubmit = async () => {
  try {
    if (editMode.value) {
      await axios.put(`/api/v1/admin/users/${form.value.emp_no}`, form.value)
      showMsg('수정되었습니다.')
    } else {
      await axios.post('/api/v1/admin/users', form.value)
      showMsg('등록되었습니다.')
    }
    resetForm()
    fetchUsers()
  } catch (err) {
    showMsg('오류: ' + (err.response?.data?.detail || '저장 실패'), true)
  }
}

// 로그인 — URLSearchParams (OAuth2 form 형식)
const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    params.append('username', username.value)
    params.append('password', password.value)
    params.append('client_id', username.value)
    const res = await axios.post('/api/v1/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    // 토큰 저장 후 라우팅
    localStorage.setItem('token', res.data.access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
    router.replace('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '사번 또는 비밀번호가 올바르지 않습니다.'
  } finally {
    loading.value = false
  }
}
```

---

### 3. 인증 토큰 처리 (빈도: 100%)

앱 초기화 시 `main.js`에서 토큰을 axios 기본 헤더에 설정.  
로그인 성공 시에도 동일하게 헤더를 직접 갱신한다.

```javascript
// main.js: 앱 기동 시 토큰 복원
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// 로그인 성공 시 (LoginView.vue:117)
localStorage.setItem('token', res.data.access_token)
localStorage.setItem('kor_nm', res.data.kor_nm || '')
localStorage.setItem('company_nm', res.data.company_nm || '')
localStorage.setItem('is_admin', res.data.is_admin ? 'true' : 'false')
axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
```

localStorage 키 목록:
- `token` — JWT Bearer 토큰
- `kor_nm` — 사용자 한국어 성명
- `company_nm` — 소속 회사명
- `is_admin` — 관리자 여부 (`'true'`/`'false'` 문자열)

---

### 4. 세션 만료 처리 — axios 인터셉터 (main.js)

401 응답 수신 시 로그아웃 처리 후 로그인 페이지로 이동.  
로그인 API 자체의 401은 리다이렉트 제외.

```javascript
// main.js:17-33
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const isLoginRequest = error.config.url.includes('/auth/login')
      if (!isLoginRequest) {
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        router.push({ name: 'login' })
      }
    }
    return Promise.reject(error)
  }
)
```

---

### 5. 라우터 가드 패턴 (router/index.js)

token 존재 여부만으로 인증 체크. `meta: { requiresAuth: true }`가 있는 라우트에 적용.

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 인증 필요 페이지 — 토큰 없으면 로그인으로
  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login' })
  }

  // 로그인된 상태에서 login 페이지 접근 차단 (뒤로가기 방지)
  if ((to.name === 'login' || to.name === 'admin-login') && token) {
    if (from.path !== '/' && from.name) return next(false)
    return next({ name: 'home' })
  }

  next()
})
```

라우트 정의 시 인증 필요 페이지에 `meta: { requiresAuth: true }` 명시:
```javascript
{
  path: '/card-usage',
  name: 'card-usage',
  component: () => import('../views/CardUsageView.vue'),
  meta: { requiresAuth: true }
}
```

---

### 6. 에러 메시지 표시 패턴

두 가지 패턴이 공존:
- **인라인 에러**: `LoginView.vue` — `ref('')` 상태 + `<div v-if="error">` (로그인 폼용)
- **토스트 메시지**: `AdminView.vue` — `message ref` + `:class` 조건부 스타일 (CRUD 성공/실패)

```vue
<!-- 인라인 에러 (LoginView.vue) -->
<div v-if="error" class="error-container">
  <span>{{ error }}</span>
</div>

<!-- 토스트 (AdminView.vue) -->
<div v-if="message" :class="['status-toast', { error: isError }]">
  {{ message }}
</div>
```

토스트 헬퍼 함수 패턴 (AdminView.vue):
```javascript
const showMsg = (msg, isErr = false) => {
  message.value = msg
  isError.value = isErr
  setTimeout(() => { message.value = '' }, 3000)
}
```

---

### 7. CSS 설계 — 다크 테마 + scoped (빈도: 100%)

모든 컴포넌트 `<style scoped>` 사용. 전역 CSS 변수 기반 다크 테마.

```vue
<style scoped>
/* 배경: 다크 네이비 계열 */
/* --bg-main: #0f172a (slate-900) */
/* --bg-card: rgba(30, 41, 59, 0.7) (slate-800 반투명) */

.premium-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
}

/* 주요 색상 팔레트 */
/* 텍스트 기본: #ffffff */
/* 텍스트 보조: #94a3b8 (slate-400) */
/* 강조: #3b82f6 (blue-500) */
/* 에러: #f87171 (red-400) */
</style>
```

---

## 안티패턴 (하지 말 것)

### A1. 에러 묵시적 무시 (AdminView.vue:220-222)

fetch 함수에서 catch 블록이 비어 실패를 조용히 무시함.

```javascript
// 나쁜 예 — 에러를 무시
const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/v1/admin/users')
    users.value = res.data
  } catch (err) { }  // <- 에러 무시
}

// 좋은 예 — 에러 표시
const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/v1/admin/users')
    users.value = res.data
  } catch (err) {
    showMsg('데이터 조회 실패: ' + (err.response?.data?.detail || '서버 오류'), true)
  }
}
```

---

### A2. 중앙 API 서비스 레이어 없음

현재 각 컴포넌트에서 URL 문자열 (`'/api/v1/admin/users'`)을 직접 사용. URL 변경 시 전체 컴포넌트 수정 필요.  
규모 확장 시 `src/services/` 레이어 도입 권장. 현재 프로젝트 규모에서는 현행 유지.

---

### A3. localStorage에 `is_admin` 문자열 저장

```javascript
// 저장 시 문자열로 저장됨
localStorage.setItem('is_admin', res.data.is_admin ? 'true' : 'false')

// 읽을 때 비교 주의 — 아래처럼 읽으면 항상 truthy
const isAdmin = localStorage.getItem('is_admin')  // 'false'도 truthy!

// 올바른 비교
const isAdmin = localStorage.getItem('is_admin') === 'true'
```

---

## 실제 코드 샘플

- `frontend/src/main.js:11-33` — axios 기본 헤더 설정 + 401 인터셉터
- `frontend/src/router/index.js:61-82` — beforeEach 인증 가드
- `frontend/src/views/LoginView.vue:77-129` — script setup 구조 + URLSearchParams 로그인
- `frontend/src/views/LoginView.vue:113-117` — 로그인 성공 시 localStorage + axios 헤더 설정
- `frontend/src/views/AdminView.vue:192-235` — ref 상태 선언 + CRUD async 패턴
- `frontend/src/views/AdminView.vue:220-222` — 에러 무시 안티패턴

---

## 신규 Vue 컴포넌트 작성 가이드

1. `frontend/src/views/{FeatureName}View.vue` 파일 생성
2. `<script setup>` 블록 사용 (Options API 금지)
3. 필요한 상태는 `ref()` 선언 — Pinia store 현재 미사용, 추가 불필요
4. API 호출은 `async/await + try/catch` — catch에서 반드시 에러 처리
5. 인증 필요 뷰라면 `router/index.js`에 `meta: { requiresAuth: true }` 추가
6. `<style scoped>` 사용, 다크 테마 팔레트 (`#0f172a`, `rgba(30,41,59,0.7)`, `#3b82f6`) 준수
7. 성공/실패 피드백은 토스트(`showMsg`) 또는 인라인 에러(`ref('')`) 중 선택
