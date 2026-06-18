# 인증 API — /api/v1/auth

**파일**: `backend/app/api/auth.py`

---

## POST /api/v1/auth/login

사번과 비밀번호로 JWT 액세스 토큰을 발급합니다.

**인증 필요**: 없음 (공개 엔드포인트)

### 요청

```
Content-Type: application/x-www-form-urlencoded
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| username | string | 필수 | 사번 (예: BP12345) |
| password | string | 필수 | 비밀번호 |
| client_id | string | 필수 | 사번과 동일값 전달 (OAuth2 형식 맞춤) |

### 응답 (200 OK)

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "kor_nm": "홍길동",
  "company_nm": "HD현대",
  "is_admin": false
}
```

### 오류 응답

| 상태 코드 | 설명 |
|---------|------|
| 401 | 사번 또는 비밀번호 불일치 |

### 처리 흐름

```
login_for_access_token()
  → mssql.authenticate_mssql_user(emp_no, password)  [MFS_USERS 조회 + 비밀번호 검증]
  → mssql.get_mssql_user_info(target_pernr)          [인사 정보 조회]
  → auth.create_access_token({sub, target_pernr, is_admin})
```

### Vue 호출 예시

```javascript
const params = new URLSearchParams()
params.append('username', username.value)
params.append('password', password.value)
params.append('client_id', username.value)

const res = await axios.post('/api/v1/auth/login', params, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
})

localStorage.setItem('token', res.data.access_token)
axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
```

---

## POST /api/v1/auth/delegate

관리자가 특정 임직원의 사번으로 대리 조회 토큰을 발급합니다.  
발급된 토큰으로 카드 이용내역 등을 조회하면 해당 임직원의 데이터를 조회합니다.

**인증 필요**: 예 (관리자 토큰)

### 요청

```json
{
  "target_pernr": "BP67890"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| target_pernr | string | 필수 | 조회 대상 임직원 사번 |

### 응답 (200 OK)

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "kor_nm": "김철수",
  "company_nm": "HD현대",
  "is_admin": true
}
```

발급된 토큰의 페이로드:
```json
{
  "sub": "BP12345",        // 실제 로그인 관리자 사번
  "target_pernr": "BP67890",  // 대리 조회 대상 사번
  "is_admin": true
}
```

### 오류 응답

| 상태 코드 | 설명 |
|---------|------|
| 403 | 관리자 권한 없음 |
| 404 | 대상 사번 사용자를 찾을 수 없음 |

### 처리 흐름

```
delegate_target_user()
  → get_current_user()  [현재 토큰에서 is_admin 확인]
  → is_admin 아니면 403 반환
  → mssql.get_mssql_user_info(target_pernr)
  → create_access_token({sub: admin_pernr, target_pernr: target})
```

---

## JWT 토큰 구조

```json
{
  "sub": "BP12345",          // 실제 로그인 사번
  "target_pernr": "BP12345", // SAP/DB 조회에 사용할 사번 (대리 조회 시 다름)
  "is_admin": false,
  "exp": 1748000000
}
```

**만료 시간**: 20분 (`ACCESS_TOKEN_EXPIRE_MINUTES`)

**토큰 갱신**: 별도 refresh token 없음. 만료 시 재로그인 필요.

---

## axios 인터셉터 (세션 만료 처리)

```javascript
// frontend/src/main.js
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
