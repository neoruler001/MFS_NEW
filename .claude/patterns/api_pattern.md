# API Pattern — MFS FastAPI 엔드포인트 컨벤션

추출 시각: 2026-06-11
샘플 파일 수: 5 (auth.py, card_usage.py, admin.py, notice.py, main.py)
신뢰도: HIGH (패턴 일관성 90% 이상)

---

## 올바른 패턴

### 1. 라우터 선언 (빈도: 100%, 5/5)

모든 도메인 파일에서 `APIRouter()`를 파라미터 없이 선언하고, prefix와 tags는 `main.py`에서 일괄 부여한다.

```python
# 도메인 파일 (예: card_usage.py)
from fastapi import APIRouter, Depends, HTTPException
router = APIRouter()

# main.py에서 prefix/tags 부여
app.include_router(card_usage.router, prefix=f"{settings.API_V1_STR}/cards", tags=["cards"])
app.include_router(auth.router,       prefix=f"{settings.API_V1_STR}/auth",  tags=["auth"])
app.include_router(admin.router,      prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
```

현재 등록된 라우터 prefix 목록:
- `/api/v1/auth` — 인증
- `/api/v1/cards` — 법인카드 이용내역
- `/api/v1/notices` — 공지사항
- `/api/v1/budget` — 예산
- `/api/v1/contacts` — 연락처
- `/api/v1/admin` — 관리자

---

### 2. 엔드포인트 함수 시그니처 (빈도: 100%, 5/5)

`current_user = Depends(get_current_user)`는 모든 인증 필요 엔드포인트의 **마지막 파라미터**에 위치한다.

```python
# GET — 조회 엔드포인트 (동기 def, SAP/DB I/O 포함)
@router.get("/usages")
def read_card_usages(
    card_num: str = "",
    fr_date: str = "",
    current_user = Depends(get_current_user)
):
    ...

# POST — 처리 엔드포인트 (동기 def, Pydantic 바디)
@router.post("/process")
def process_expenses(
    req: ProcessRequestSchema,
    current_user = Depends(get_current_user)
):
    ...

# POST — 인증 엔드포인트 (비동기 async def, response_model 명시)
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    ...
```

`async def` 사용 기준:
- `auth.py`의 login, delegate — OAuth2 폼 처리, 토큰 발급
- 그 외 SAP/DB I/O가 있는 엔드포인트 — **동기 `def`** 사용 (pymssql, requests가 동기 라이브러리이므로)

---

### 3. 예외 처리 (빈도: 95%, 19/20 엔드포인트)

외부 I/O (SAP, DB)는 `try/except → HTTPException(status_code=500)` 패턴으로 처리한다.  
비즈니스 규칙 위반은 `HTTPException`에 구체적인 status_code를 명시한다.

```python
# 외부 I/O 실패 (500)
try:
    result = call_xfi00250(params)
    return result.get('TE_CARD_USE', [])
except Exception as e:
    print(f"[DEBUG] API Error: {e}")
    raise HTTPException(status_code=500, detail="요청 처리 중 서버 오류가 발생했습니다.")

# 인증 실패 (401)
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="사번 또는 비밀번호가 올바르지 않습니다.",
    headers={"WWW-Authenticate": "Bearer"},
)

# 권한 없음 (403)
if not current_user.is_admin:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자만 사용할 수 있습니다.")

# 리소스 없음 (404)
if not target_info:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 사번의 사용자를 찾을 수 없습니다.")

# 입력값 오류 (400)
if len(req.items) > 100:
    raise HTTPException(status_code=400, detail="한 번에 최대 100건까지만 처리 가능합니다.")
```

로깅: 현재 `print(f"[DEBUG] ...")` 방식 사용. 운영 전환 시 `logging` 모듈로 교체 필요.

---

### 4. Pydantic 스키마 선언 방식 (빈도: 100%, 5/5)

인라인 스키마 선언 — 도메인 파일 상단에 `BaseModel` 서브클래스로 선언한다.  
응답 모델은 `auth.py`의 Token 제외 대부분 `dict` 직접 반환.

```python
# 인라인 요청 스키마 (card_usage.py 패턴)
from pydantic import BaseModel
from typing import List, Optional

class CardItemSchema(BaseModel):
    BUKRS: str
    APPR_DATE: str
    CARD_NUMC: str
    APPR_NUMC: str
    CANC_FLAG: str = ""    # 선택 필드는 기본값 제공
    SGTXT: str = ""

class ProcessRequestSchema(BaseModel):
    items: List[CardItemSchema]

# 인라인 관리자 스키마 (admin.py 패턴)
class UserUpdate(BaseModel):
    kor_nm: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

# 응답: dict 직접 반환 (response_model 미지정이 현재 표준)
return {
    "PE_RESULT": result.get("PE_RESULT", ""),
    "PE_MESSAGE": result.get("PE_MESSAGE", "처리가 완료되었습니다."),
    "T_DATA": result.get("T_DATA", []) or [],
}
```

---

### 5. CORS 및 미들웨어 설정 (main.py)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 개발 환경 — 운영 시 특정 도메인으로 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 6. SAP 결과 + DB 데이터 병합 응답 패턴 (notice.py)

내부 MSSQL 데이터와 SAP 데이터를 병합해 단일 응답으로 반환하는 패턴.  
내부 데이터가 앞 순서로 배치된다.

```python
@router.get("/notices")
def read_notices(current_user = Depends(get_current_user)):
    # 1. MSSQL 조회
    internal_data = get_internal_notices()
    formatted_internal = [...]

    # 2. SAP 조회 (예외 발생해도 내부 데이터는 반환)
    sap_notices = []
    try:
        result = call_xfi00320({"PERNR": current_user.target_pernr})
        if result and "ZFIXT405_1" in result:
            sap_notices = result["ZFIXT405_1"] or []
    except Exception as e:
        print(f"SAP Notice Error: {e}")

    # 3. 병합 반환
    return formatted_internal + sap_notices
```

---

## 안티패턴 (하지 말 것)

### A1. check_admin() 빈 함수 — 보안 검증 우회 (admin.py:35)

```python
# 위험: 함수 본문이 pass로 비어 있어 권한 체크가 실제로 이루어지지 않음
def check_admin(current_user: any):
    if not getattr(current_user, "is_admin", False):
        pass  # <- 여기서 예외를 발생시키지 않으므로 관리자 아닌 사람도 통과
    return True
```

올바른 패턴: `delegate` 엔드포인트처럼 `HTTPException(403)` 즉시 raise

```python
def check_admin(current_user):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="관리자만 사용할 수 있습니다.")
```

위험도: CRITICAL — `/api/v1/admin/*` 엔드포인트들이 실질적으로 비인증 접근 허용 상태

---

### A2. 스키마 이름 충돌 (admin.py vs schemas.py)

`admin.py`의 인라인 `UserCreate`와 `schemas.py`의 `UserCreate`가 동일한 이름으로 충돌 가능.  
명명 규칙: 인라인 스키마는 도메인 접두사를 붙인다.

```python
# 나쁜 예
class UserCreate(BaseModel): ...   # admin.py에도, schemas.py에도 동일 이름

# 좋은 예
class AdminUserCreate(BaseModel): ...   # admin.py 전용 스키마
```

---

### A3. allow_origins=["*"] (main.py:17)

운영 환경에서는 특정 도메인으로 제한해야 한다.

```python
# 운영 시
allow_origins=["https://mfs.yourdomain.com"]
```

---

## 실제 코드 샘플

- `backend/app/api/auth.py:19` — `response_model=Token` 적용 사례 (로그인 엔드포인트)
- `backend/app/api/auth.py:80-110` — 403/404 HTTPException 패턴
- `backend/app/api/card_usage.py:49-91` — try/except + print 로그 패턴
- `backend/app/api/card_usage.py:151-155` — 400 입력값 검증 패턴
- `backend/app/api/admin.py:35-41` — check_admin 빈 함수 (안티패턴)
- `backend/app/api/admin.py:55-72` — DML 표준 try/except/finally 패턴
- `backend/app/api/notice.py:10-42` — MSSQL + SAP 병합 응답 패턴
- `backend/app/main.py:23-28` — 라우터 등록 패턴

---

## 신규 API 엔드포인트 작성 가이드

1. 도메인 파일(`backend/app/api/{domain}.py`) 생성
2. 파일 상단에 `router = APIRouter()` 선언 (prefix/tags 미지정)
3. 요청 바디가 있는 경우 해당 파일 상단에 Pydantic `BaseModel` 인라인 선언 — 이름에 도메인 접두사 붙이기
4. `Depends(get_current_user)`를 마지막 파라미터로 배치
5. SAP/DB I/O는 반드시 `try/except → HTTPException(status_code=500)` 감싸기
6. 권한 체크 필요 시 함수 진입 직후 `if not current_user.is_admin: raise HTTPException(403)` 패턴
7. `main.py`에 `app.include_router(...)` 추가하여 등록
