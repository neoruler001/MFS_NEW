---
name: scaffold-feature
description: 추출된 MFS 프로젝트 컨벤션에 따라 신규 기능을 스캐폴딩한다(FastAPI 라우터, 서비스 함수, DB/SAP 연동, Vue 컴포넌트까지). "[기능명] 기능 추가해줘", "새 API 만들어줘", "scaffold feature", "패턴대로 만들어줘", "신규 모듈 생성", "보일러플레이트 생성", "새 엔드포인트 추가", "Vue 뷰 새로 만들어줘" 요청 시 트리거.
model: sonnet
---

# Scaffold Feature — MFS 컨벤션 기반 신규 기능 생성

## 트리거

- "[기능명] 기능 추가해줘"
- "새 API 엔드포인트 만들어줘"
- "패턴대로 만들어줘"
- "신규 Vue 뷰 컴포넌트 만들어줘"
- "scaffold feature", "보일러플레이트 생성"
- "FastAPI 라우터 새로 추가해줘"

## 실행 방법

`harness-ito:scaffold-feature` 에이전트를 호출하여 MFS 컨벤션에 맞는 파일 세트를 생성한다.

실행 전 `.claude/patterns/*.md` 파일들을 로드하여 컨벤션을 확인한다.

## MFS 특화 컨텍스트

### 백엔드 — FastAPI 라우터 패턴

신규 API 도메인 추가 시 생성할 파일 체크리스트:

**1. `backend/app/api/{도메인}.py` (라우터)**
```python
from fastapi import APIRouter, Depends, HTTPException
from ..core.auth import get_current_user
from ..core.mssql import get_mssql_connection  # MSSQL 필요 시
from ..core.soap_client import call_xfi*       # SAP 필요 시

router = APIRouter()

@router.get("/{경로}")
def {함수명}(current_user = Depends(get_current_user)):
    try:
        # 비즈니스 로직
        return result
    except Exception as e:
        print(f"[{도메인}] 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**2. `backend/app/main.py` — 라우터 등록 추가**
```python
from .api.{도메인} import router as {도메인}_router
app.include_router({도메인}_router, prefix="/api/v1/{경로}", tags=["{도메인}"])
```

**3. Pydantic 스키마 (필요 시)**
- 간단한 스키마는 api 파일 내 인라인 정의 (기존 패턴)
- 공통 스키마는 `backend/app/schemas/schemas.py`에 추가

### MSSQL 직접 쿼리 패턴

```python
def {함수명}(param: str):
    conn = get_mssql_connection()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT ... FROM {테이블} WHERE COL = %s", (param,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise
    finally:
        conn.close()
```

DML (INSERT/UPDATE/DELETE) 시:
```python
conn = get_mssql_connection()
try:
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return {"message": "성공"}
except Exception as e:
    conn.rollback()
    raise HTTPException(status_code=500, detail=str(e))
finally:
    conn.close()
```

### SAP SOAP 호출 패턴

```python
from ..core.soap_client import _call_sap_soap

def call_xfi{번호}(params: dict) -> dict:
    xml_body = f"""
    <PI_{파라미터}>{params['키']}</PI_{파라미터}>
    """
    result = _call_sap_soap("XFI{번호}", xml_body)
    return result
```

### 프런트엔드 — Vue 3 컴포넌트 패턴

**`frontend/src/views/{기능}View.vue`**
```vue
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const data = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/{경로}')
    data.value = response.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
```

**`frontend/src/router/index.js` — 라우트 추가**
```javascript
{
  path: '/{경로}',
  name: '{기능}',
  component: () => import('../views/{기능}View.vue'),
  meta: { requiresAuth: true }
}
```

### 파일 생성 순서 권장
1. `backend/app/api/{도메인}.py` (라우터 + 엔드포인트)
2. `backend/app/main.py` (라우터 등록)
3. `backend/app/core/mssql.py` 또는 `soap_client.py` (서비스 함수 추가)
4. `frontend/src/views/{기능}View.vue` (UI 컴포넌트)
5. `frontend/src/router/index.js` (라우트 등록)

### 주의사항
- 모든 보호 엔드포인트에 `Depends(get_current_user)` 필수
- 에러 처리: `try/except → HTTPException(status_code=500)` + `print()` 로그 (기존 패턴)
- 응답 형식: `dict` 직접 반환 (기존 패턴 — Pydantic 응답 모델 선택적)
- admin 전용 기능은 `is_admin` 체크 로직 반드시 추가 (`check_admin()` 미사용)
