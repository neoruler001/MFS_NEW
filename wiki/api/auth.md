# 인증 API

**Base path:** `/api/v1/auth`

---

## POST /login

사번과 비밀번호로 JWT 액세스 토큰을 발급한다.

**파일:** `backend/app/api/auth.py` → `login_for_access_token()`

### 요청

```
Content-Type: application/x-www-form-urlencoded
```

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `username` | string | ✓ | 사번 (EMP_NO) |
| `password` | string | ✓ | 비밀번호 |
| `client_id` | string | ✗ | 클라이언트 구분자 (현재 미검증) |

### 응답 (200)

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "kor_nm": "홍길동",
  "company_nm": "HD현대",
  "is_admin": false
}
```

### 내부 처리 흐름

```python
# 1. MSSQL MFS_USERS에서 사번/패스워드 확인
user = mssql.authenticate_mssql_user(emp_no, password)
# → SELECT * FROM MFS_USERS WHERE EMP_NO = %s
# → pbkdf2_sha256 해시 비교

# 2. 인사 정보 조회
info = mssql.get_mssql_user_info(target_pernr)
# → SELECT COMPANY, COMPANY_NM, EMP_NO, KOR_NM, OFFI_RES_NM
#   FROM SUPPORT.DBO.ALL_AMSTM_VIEW WHERE EMP_NO = %s

# 3. JWT 생성 (20분 만료)
token = create_access_token({
    "sub": emp_no,
    "target_pernr": emp_no,
    "is_admin": is_admin
})
```

### 오류

| 코드 | 상황 |
|------|------|
| 400 | 사번 또는 비밀번호 오류 |
| 500 | MSSQL 연결 실패 |

---

## POST /delegate

관리자가 특정 사원의 법인카드를 대리 조회하기 위한 위임 토큰 발급.

**파일:** `backend/app/api/auth.py` → `delegate_target_user()`

> **관리자 토큰 필요** — `is_admin: true` JWT만 허용

### 요청

```json
{
  "target_pernr": "BP26745"
}
```

### 응답 (200)

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "kor_nm": "김철수",
  "company_nm": "HD현대중공업"
}
```

### 내부 처리

새 JWT의 `target_pernr` 클레임에 대상 사번이 설정된다. 이후 카드/예산 조회 시 FastAPI 라우터들이 이 값을 SAP 파라미터로 사용한다.

---

## 인증 방식 (JWT)

모든 보호 엔드포인트는 `Depends(get_current_user)` 를 통해 검증된다.

```python
# backend/app/core/auth.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    username = payload.get("sub")
    target_pernr = payload.get("target_pernr")
    is_admin = payload.get("is_admin", False)
    ...
```

**헤더 형식:**
```
Authorization: Bearer eyJhbGci...
```

**토큰 만료:** 20분 (`ACCESS_TOKEN_EXPIRE_MINUTES`)

> **Vue 측 처리:** `frontend/src/main.js`의 axios 응답 인터셉터가 401 수신 시 localStorage 초기화 후 `/login`으로 리다이렉트
