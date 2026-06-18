# 보안 이슈

> 운영 배포 전 반드시 해결해야 할 항목입니다. HIGH 등급은 긴급 조치가 필요합니다.

---

## HIGH — 즉시 조치 필요

### 1. MSSQL 자격증명 소스코드 하드코딩

| 항목 | 내용 |
|------|------|
| 위치 | `backend/app/core/config.py`, `backend/app/db/mssql_db.py` |
| 위험 | DB 서버 IP, 포트, 계정, 비밀번호가 소스코드에 평문 기재 |
| 영향 | 소스코드 유출 시 운영 DB 직접 접근 가능 |

**조치 방법**:

```python
# 현재 (위험)
MSSQL_HOST = "10.100.37.178"
MSSQL_USER = "XB01"
MSSQL_PASSWORD = "***"

# 권장 — pydantic-settings + .env 파일
class Settings(BaseSettings):
    MSSQL_HOST: str
    MSSQL_USER: str
    MSSQL_PASSWORD: str

    class Config:
        env_file = ".env"
```

---

### 2. SAP PI 자격증명 소스코드 하드코딩

| 항목 | 내용 |
|------|------|
| 위치 | `backend/app/core/soap_client.py` 상단 |
| 위험 | SAP PI 접속 계정(INFPIUSR)과 비밀번호가 소스코드에 평문 기재 |

**조치 방법**:

```python
# 현재 (위험)
SAP_USER = "INFPIUSR"
SAP_PASS = "http01"

# 권장
from app.core.config import settings
SAP_USER = settings.SAP_USER
SAP_PASS = settings.SAP_PASS
```

---

### 3. Admin API 권한 체크 무효

| 항목 | 내용 |
|------|------|
| 위치 | `backend/app/api/admin.py:35-41` |
| 위험 | 관리자 권한 체크 함수가 실질적으로 아무 동작도 하지 않음 |
| 영향 | 인증된 **일반 사용자**도 `/api/v1/admin/*` 전체 엔드포인트 접근 가능 |

```python
# 현재 코드 (심각한 취약점)
def check_admin(current_user: any):
    if not getattr(current_user, "is_admin", False):
        pass   # ← 예외를 발생시키지 않음!
    return True
```

**올바른 패턴**:

```python
def check_admin(current_user):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 사용할 수 있습니다."
        )
```

> 이 취약점으로 인해 모든 `/api/v1/admin/users`, `/api/v1/admin/notices`, `/api/v1/admin/contacts` 엔드포인트가 무방비 상태입니다.

---

### 4. JWT SECRET_KEY 기본값 노출

| 항목 | 내용 |
|------|------|
| 위치 | `backend/app/core/config.py` |
| 위험 | 기본값이 `"SuperSecretKeyForDevelopmentOnly"` — 운영 배포 시 이 값으로 토큰 위조 가능 |

**조치 방법**: `.env` 파일에 충분한 길이(32자 이상)의 무작위 SECRET_KEY 설정

```bash
# 안전한 SECRET_KEY 생성 (Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## MEDIUM — 운영 전 검토 필요

### 5. CORS 전체 허용

| 항목 | 내용 |
|------|------|
| 위치 | `backend/app/main.py` |
| 위험 | `allow_origins=["*"]` — 모든 도메인에서 API 접근 허용 |

```python
# 현재
allow_origins=["*"]

# 운영 시
allow_origins=["https://mfs.yourdomain.com"]
```

---

### 6. 인덱스 파일 내 자격증명 평문 기재

| 항목 | 내용 |
|------|------|
| 위치 | `_workspace/index/env_branches.json`, `_workspace/index/external_io.json` |
| 위험 | 하네스 분석 과정에서 추출된 실제 DB/SAP 자격증명이 JSON 파일에 기재 |

**권장 조치**:
1. `_workspace/` 디렉토리를 `.gitignore`에 추가
2. 해당 JSON 파일의 패스워드 값을 `[DB_PASSWORD]`, `[SAP_PASSWORD]` 플레이스홀더로 교체

---

### 7. 프런트엔드 localStorage 기반 권한 관리

| 항목 | 내용 |
|------|------|
| 위치 | `frontend/src/views/*.vue` |
| 위험 | `localStorage.getItem('is_admin')` 기반으로 관리자 UI 노출 여부 결정 — 클라이언트 조작 가능 |

> 프런트엔드 UI 제어 목적으로는 허용 범위이나, 서버 API가 별도로 권한 검증을 해야 합니다 (#3 이슈와 연관).

---

### 8. is_admin 문자열 비교 오류 가능성

```javascript
// 저장 시: 문자열로 저장됨
localStorage.setItem('is_admin', 'false')

// 읽을 때 주의 — 'false'도 truthy!
const isAdmin = localStorage.getItem('is_admin')  // 'false' (truthy)

// 올바른 비교
const isAdmin = localStorage.getItem('is_admin') === 'true'
```

---

## LOW — 코드 품질 개선

### 9. print() 기반 디버그 로그

`print(f"[DEBUG] ...")` 패턴이 API 레이어 전반에 산재합니다. 운영 환경에서 `logging` 모듈로 교체가 필요합니다.

```python
# 현재
print(f"[DEBUG] API Error: {e}")

# 권장
import logging
logger = logging.getLogger(__name__)
logger.error(f"API Error: {e}")
```

---

## 보안 조치 우선순위

| 우선순위 | 항목 | 난이도 |
|---------|------|--------|
| 1 | Admin API 권한 체크 수정 (#3) | 낮음 (코드 2줄 변경) |
| 2 | JWT SECRET_KEY 환경변수화 (#4) | 낮음 |
| 3 | MSSQL 자격증명 환경변수화 (#1) | 중간 |
| 4 | SAP 자격증명 환경변수화 (#2) | 낮음 |
| 5 | _workspace/ .gitignore 추가 (#6) | 낮음 |
| 6 | CORS 도메인 제한 (#5) | 낮음 |
