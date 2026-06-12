# 코드 컨벤션

---

## FastAPI 백엔드

### 라우터 선언

```python
# ✅ 올바른 패턴: APIRouter() 파라미터 없이 선언, prefix/tags는 main.py에서 부여
router = APIRouter()

@router.get("/usages")
def read_card_usages(...):
    ...

# main.py에서 prefix 부여
app.include_router(card_usage.router, prefix="/api/v1/cards", tags=["cards"])
```

### 엔드포인트 함수 시그니처

```python
# ✅ 올바른 패턴: current_user는 항상 마지막 파라미터
@router.get("/usages")
def read_card_usages(
    fr_date: str,
    to_date: str,
    pi_status: str = "",
    current_user = Depends(get_current_user)   # ← 항상 마지막
):
    ...
```

### 동기 vs 비동기

```python
# ✅ SAP/DB I/O는 동기 def (실제 패턴)
@router.get("/usages")
def read_card_usages(...):
    result = soap_client.call_xfi00250(...)  # 동기 IO

# ✅ 인증 엔드포인트만 async def
@router.post("/login")
async def login_for_access_token(...):
    ...
```

### 예외 처리

```python
# ✅ 올바른 패턴
try:
    result = soap_client.call_xfi00250(params)
except Exception as e:
    print(f"Error: {e}")
    raise HTTPException(status_code=500, detail="카드 조회 오류")
```

> **주의:** 현재 `logging` 모듈 미사용 — `print`로 로깅. 신규 코드는 `logging` 사용 권장.

### DI (Dependency Injection)

```python
# ✅ 모든 보호 엔드포인트에 적용
current_user = Depends(get_current_user)

# current_user 속성
current_user.username       # 사번 (EMP_NO, JWT sub)
current_user.target_pernr   # 조회 대상 사번 (대리조회 시 다름)
current_user.is_admin       # 관리자 여부
```

---

## Vue 3 프런트엔드

### Composition API

```vue
<!-- ✅ 전체 <script setup> 패턴 -->
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const data = ref([])

onMounted(async () => {
  const res = await axios.get('/api/v1/cards/usages')
  data.value = res.data
})
</script>
```

### Axios 호출

```javascript
// ✅ main.js 인터셉터가 Authorization 헤더를 자동 설정
// → 개별 컴포넌트에서 헤더 설정 불필요
const res = await axios.get('/api/v1/cards/usages', {
  params: { fr_date, to_date, pi_status }
})

// ❌ 안티패턴: 개별 헤더 설정 (인터셉터 우회)
const res = await axios.get('/api/v1/cards/usages', {
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
})
```

### 관리자 판별

```javascript
// ✅ 올바른 패턴
const isAdmin = localStorage.getItem('is_admin') === 'true'

// ❌ 안티패턴: 문자열 'false'도 truthy
const isAdmin = localStorage.getItem('is_admin')  // 'false' → truthy!
```

---

## MSSQL 쿼리 패턴

### SELECT

```python
# ✅ try/finally(close) — rollback 불필요
def get_internal_notices():
    conn = get_mssql_connection()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute("SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC")
        return cursor.fetchall()
    finally:
        conn.close()
```

### DML (INSERT/UPDATE/DELETE)

```python
# ✅ try/except(rollback)/finally(close) 100% 일관
def create_admin_user(emp_no, kor_nm, pwd_hash, is_admin):
    conn = get_mssql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO MFS_USERS (EMP_NO, KOR_NM, PASSWORD_HASH, IS_ADMIN) VALUES (%s,%s,%s,%s)",
            (emp_no, kor_nm, pwd_hash, is_admin)
        )
        conn.commit()
        return {"message": "생성 완료"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
```

### 레거시 import 금지

```python
# ❌ 안티패턴: 레거시 파일 import
from app.db.mssql_db import get_mssql_connection  # 레거시

# ✅ 올바른 import
from app.core.mssql import get_mssql_connection   # 실사용 버전
```

---

## SAP SOAP 호출 패턴

```python
# ✅ 항상 _call_sap_soap() 경유
result = _call_sap_soap("XFI00250", xml_body)

# ❌ 안티패턴: requests.post 직접 호출
response = requests.post(SAP_PI_URL, ...)  # 인증/헤더 누락 위험

# ✅ 빈 결과 방어
result = soap_client.call_xfi00250(params)
if not result:
    raise HTTPException(status_code=502, detail="SAP 조회 실패")
```

---

## 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| Python 함수/변수 | snake_case | `get_current_user`, `target_pernr` |
| Python 클래스 | PascalCase | `Settings`, `User` |
| Vue 컴포넌트 | PascalCase | `CardUsageView.vue` |
| API 경로 | kebab-case | `/api/v1/cards/worklist` |
| MSSQL 컬럼 | UPPER_CASE | `EMP_NO`, `KOR_NM` |
