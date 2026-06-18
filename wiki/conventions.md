# 코드 컨벤션 가이드

## 백엔드 (FastAPI)

### 라우터 선언

모든 도메인 파일에서 `APIRouter()`를 파라미터 없이 선언하고, prefix/tags는 `main.py`에서 일괄 부여합니다.

```python
# 도메인 파일 (예: card_usage.py)
from fastapi import APIRouter, Depends, HTTPException
router = APIRouter()

# main.py에서 등록
app.include_router(card_usage.router, prefix=f"{settings.API_V1_STR}/cards", tags=["cards"])
```

현재 등록된 라우터 prefix:
- `/api/v1/auth` — 인증
- `/api/v1/cards` — 법인카드
- `/api/v1/notices` — 공지사항
- `/api/v1/budget` — 예산
- `/api/v1/contacts` — 연락처
- `/api/v1/admin` — 관리자

---

### 엔드포인트 함수 시그니처

`Depends(get_current_user)`는 모든 인증 필요 엔드포인트의 **마지막 파라미터**에 위치합니다.

```python
# GET — 조회 (동기 def, SAP/DB I/O 포함)
@router.get("/usages")
def read_card_usages(
    card_num: str = "",
    fr_date: str = "",
    current_user = Depends(get_current_user)  # 마지막에 위치
):
    ...

# POST — 처리 (동기 def, Pydantic 바디)
@router.post("/process")
def process_expenses(
    req: ProcessRequestSchema,
    current_user = Depends(get_current_user)
):
    ...
```

**async/sync 사용 기준**:
- `async def`: auth.py의 login, delegate (OAuth2 폼 처리)
- `def` (동기): SAP/MSSQL I/O가 있는 엔드포인트 (pymssql, requests가 동기 라이브러리)

---

### 예외 처리

```python
# 외부 I/O 실패 (500)
try:
    result = call_xfi00250(params)
    return result.get('TE_CARD_USE', [])
except Exception as e:
    print(f"[DEBUG] API Error: {e}")
    raise HTTPException(status_code=500, detail="요청 처리 중 서버 오류가 발생했습니다.")

# 인증 실패 (401)
raise HTTPException(status_code=401, detail="사번 또는 비밀번호가 올바르지 않습니다.",
                    headers={"WWW-Authenticate": "Bearer"})

# 권한 없음 (403)
if not current_user.is_admin:
    raise HTTPException(status_code=403, detail="관리자만 사용할 수 있습니다.")

# 리소스 없음 (404)
if not target_info:
    raise HTTPException(status_code=404, detail="해당 사번의 사용자를 찾을 수 없습니다.")
```

---

### Pydantic 스키마

인라인 선언 방식 — 도메인 파일 상단에 선언합니다. 이름에 도메인 접두사를 붙입니다.

```python
# card_usage.py 패턴
class CardItemSchema(BaseModel):
    BUKRS: str
    APPR_DATE: str
    CARD_NUMC: str
    APPR_NUMC: str
    CANC_FLAG: str = ""    # 선택 필드는 기본값 제공
    SGTXT: str = ""

class ProcessRequestSchema(BaseModel):
    items: List[CardItemSchema]
```

응답 모델: 대부분 `dict` 직접 반환 (auth.py의 `Token` 제외).

---

### MSSQL + SAP 병합 응답 패턴 (notice.py)

```python
@router.get("/notices")
def read_notices(current_user = Depends(get_current_user)):
    # 1. MSSQL 조회
    internal_data = get_internal_notices()

    # 2. SAP 조회 (실패해도 내부 데이터는 반환)
    sap_notices = []
    try:
        result = call_xfi00320({"PERNR": current_user.target_pernr})
        if result and "ZFIXT405_1" in result:
            sap_notices = result["ZFIXT405_1"] or []
    except Exception as e:
        print(f"SAP Notice Error: {e}")

    # 3. 내부 데이터 앞에 배치하여 병합
    return formatted_internal + sap_notices
```

---

### 신규 API 엔드포인트 체크리스트

1. `backend/app/api/{domain}.py` 파일 생성
2. 파일 상단에 `router = APIRouter()` 선언
3. 요청 바디 필요 시 해당 파일 상단에 Pydantic `BaseModel` 인라인 선언 (도메인 접두사)
4. `Depends(get_current_user)` 마지막 파라미터로 배치
5. SAP/DB I/O는 `try/except → HTTPException(500)` 감싸기
6. 권한 체크 필요 시: `if not current_user.is_admin: raise HTTPException(403)`
7. `main.py`에 `app.include_router(...)` 추가

---

## 데이터베이스 (MSSQL)

### 함수 위치 규칙

| 역할 | 위치 |
|------|------|
| 공통 연결 생성기 | `backend/app/core/mssql.py` |
| SELECT 공통 함수 | `backend/app/core/mssql.py` |
| DML (CRUD) | `backend/app/api/admin.py` 엔드포인트 내 인라인 |

> `backend/app/db/mssql_db.py` — 레거시. 신규 코드에서 사용 금지.

### SELECT 패턴

```python
def get_internal_notices():
    conn = get_mssql_connection()
    if not conn: return []           # None 체크 필수
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC")
        return cursor.fetchall()
    finally:
        conn.close()                 # 항상 close
```

### DML 트랜잭션 패턴

```python
conn = get_mssql_connection()
if not conn:
    raise HTTPException(status_code=500, detail="DB 연결 실패")
try:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO MFS_USERS ... VALUES (%s, %s)", (val1, val2))
    conn.commit()
    return {"message": "등록되었습니다."}
except Exception as e:
    conn.rollback()
    raise HTTPException(status_code=400, detail=str(e))
finally:
    conn.close()
```

---

## SAP SOAP

### 신규 인터페이스 추가 패턴

```python
# core/soap_client.py 하단에 추가
def call_xfi{번호}(params: dict) -> Dict:
    inner_xml = f"""<ns:MT_XFI{번호}_LEGY>
         <PI_{파라미터1}>{params.get('PI_{파라미터1}', '')}</PI_{파라미터1}>
      </ns:MT_XFI{번호}_LEGY>"""
    return _call_sap_soap("XFI{번호}", inner_xml)
```

배열 입력 시 XFI00260/270의 `<T_DATA>` 반복 구조 참고.

**응답 접근 방어 패턴**:

```python
result = call_xfi00250(params)
rows = result.get('TE_CARD_USE', []) or []   # None도 []로 변환
```

---

## 프런트엔드 (Vue 3)

### 컴포넌트 구조

모든 컴포넌트가 `<script setup>` 방식의 Composition API를 사용합니다. Options API 미사용.

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const items = ref([])

onMounted(() => {
  fetchItems()
})

const fetchItems = async () => {
  try {
    const res = await axios.get('/api/v1/...')
    items.value = res.data
  } catch (err) {
    showMsg('조회 실패: ' + (err.response?.data?.detail || '서버 오류'), true)
  }
}
</script>
```

---

### axios 호출 패턴

```javascript
// 조회 패턴
const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/v1/admin/users')
    users.value = res.data
  } catch (err) {
    showMsg('조회 실패', true)
  }
}

// 변경 패턴
const handleSubmit = async () => {
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
```

---

### 토스트 메시지 패턴

```javascript
const message = ref('')
const isError = ref(false)

const showMsg = (msg, isErr = false) => {
  message.value = msg
  isError.value = isErr
  setTimeout(() => { message.value = '' }, 3000)
}
```

```html
<div v-if="message" :class="['status-toast', { error: isError }]">
  {{ message }}
</div>
```

---

### 신규 Vue 컴포넌트 체크리스트

1. `frontend/src/views/{FeatureName}View.vue` 파일 생성
2. `<script setup>` 블록 사용 (Options API 금지)
3. 상태는 `ref()` 선언 — Pinia store 미사용
4. API 호출: `async/await + try/catch` — catch 블록에서 반드시 에러 처리
5. 인증 필요 뷰: `router/index.js`에 `meta: { requiresAuth: true }` 추가
6. `<style scoped>` 사용, 다크 테마 팔레트 준수
7. `is_admin` 비교 시 반드시 `=== 'true'` 사용

---

## CSS 디자인 시스템 (다크 테마)

```css
/* 주요 색상 변수 */
--bg-main: #0f172a;                      /* slate-900 — 배경 기본 */
--bg-card: rgba(30, 41, 59, 0.7);        /* slate-800 반투명 — 카드 배경 */
--text-primary: #ffffff;
--text-secondary: #94a3b8;               /* slate-400 */
--accent: #3b82f6;                       /* blue-500 */
--error: #f87171;                        /* red-400 */
--border: rgba(255, 255, 255, 0.08);
```

```css
/* 표준 카드 컴포넌트 */
.premium-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
}
```
