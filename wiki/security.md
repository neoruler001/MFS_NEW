# 보안 이슈 & 개선 방향

> 운영 배포 전 반드시 처리해야 할 항목들. 우선순위 순서로 정렬.

---

## 🔴 CRITICAL — admin API 무방비

**위치:** `backend/app/api/admin.py:35-41`

```python
# 현재 코드 (보안 홀)
def check_admin(current_user):
    pass  # ← 아무 검증도 하지 않음

# 결과: 인증된 일반 사용자도 /api/v1/admin/* 전체 접근 가능
```

**수정 방법:**

```python
def check_admin(current_user):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="관리자 권한이 필요합니다."
        )
```

또는 FastAPI Dependency로 전환:

```python
async def require_admin(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한 필요")
    return current_user

# 사용
@router.get("/users")
def list_users(admin = Depends(require_admin)):
    ...
```

---

## 🔴 HIGH — MSSQL 자격증명 하드코딩

**위치:** `backend/app/core/config.py`

```python
# 현재 코드 (위험)
MSSQL_HOST: str = "10.100.37.178"
MSSQL_PORT: int = 3218
MSSQL_USER: str = "XB01"
MSSQL_PASSWORD: str = "DNSdudCMsoft!(0709)"  # ← 소스코드 노출
MSSQL_DB: str = "MFS"
```

**수정 방법:**

1. `backend/.env` 파일 생성 (이미 존재할 수 있음):

```bash
MSSQL_HOST=10.100.37.178
MSSQL_PORT=3218
MSSQL_USER=XB01
MSSQL_PASSWORD=실제패스워드
MSSQL_DB=MFS
```

2. `config.py` 수정 — 환경변수에서만 로드:

```python
class Settings(BaseSettings):
    MSSQL_HOST: str      # no default
    MSSQL_PORT: int      # no default
    MSSQL_USER: str      # no default
    MSSQL_PASSWORD: str  # no default
    MSSQL_DB: str        # no default

    class Config:
        env_file = ".env"
```

3. `.gitignore`에 `.env` 추가 (이미 추가됨 ✓)

---

## 🔴 HIGH — SAP PI 자격증명 하드코딩

**위치:** `backend/app/core/soap_client.py`

```python
# 현재 코드 (위험)
SAP_USER = "INFPIUSR"
SAP_PASS = "http01"        # ← 하드코딩
SAP_PI_URL = "http://hipop.hhi.co.kr:50000/..."
```

**수정 방법:**

```python
# config.py에 추가
SAP_PI_URL: str
SAP_USER: str
SAP_PASS: str

# soap_client.py 수정
from app.core.config import settings

response = requests.post(
    settings.SAP_PI_URL,
    auth=HTTPBasicAuth(settings.SAP_USER, settings.SAP_PASS),
    ...
)
```

---

## 🟡 MEDIUM — JWT SECRET_KEY 기본값

**위치:** `backend/app/core/config.py`

```python
# 현재 코드
SECRET_KEY: str = "SuperSecretKeyForDevelopmentOnly"  # ← 약한 기본값
```

**수정 방법:**

```bash
# .env에 강한 랜덤 키 생성
python -c "import secrets; print(secrets.token_hex(32))"
# → SECRET_KEY=생성된키를.env에 추가
```

---

## 🟡 MEDIUM — CORS 전체 허용

**위치:** `backend/app/main.py`

```python
# 현재 코드
allow_origins=["*"]  # ← 개발 편의용, 운영에 부적합
```

**수정 방법:**

```python
allow_origins=[
    "http://localhost:4001",
    "https://mfs.hhi.co.kr",  # 운영 도메인
]
```

---

## 🟡 MEDIUM — SAP SOAP HTTP (비암호화)

**위치:** `backend/app/core/soap_client.py`

현재 SAP PI 통신이 `http://` — 네트워크 스니핑 시 SOAP 페이로드 노출.

운영 환경에서 SAP PI가 `https://` 지원 시 전환 권장.

---

## 🟢 LOW — 동기 SAP I/O 블로킹

**위치:** `backend/app/core/soap_client.py`

`requests.post`는 동기 IO — async FastAPI 이벤트 루프를 블로킹.

고부하 시 `httpx.AsyncClient`로 전환:

```python
import httpx

async def _call_sap_soap(interface_id: str, body_content: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SAP_PI_URL,
            content=soap_envelope.encode("utf-8"),
            headers=headers,
            auth=(settings.SAP_USER, settings.SAP_PASS),
            timeout=30
        )
    ...
```

---

## 보안 개선 체크리스트

- [ ] `check_admin()` 함수 실제 검증 구현
- [ ] MSSQL 자격증명 → `.env` 이관
- [ ] SAP PI 자격증명 → `.env` 이관
- [ ] JWT SECRET_KEY 강한 랜덤값으로 교체
- [ ] CORS `allow_origins` 운영 도메인으로 제한
- [ ] `_workspace/index/env_branches.json` — 실제 값 플레이스홀더로 교체 (git 커밋 전)
