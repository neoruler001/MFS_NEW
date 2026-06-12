# 개발 환경 설정

---

## 백엔드

**요구 사항:** Python 3.14, Windows

```bash
cd backend

# 1. 가상환경 활성화
.venv\Scripts\activate       # Windows PowerShell
# 또는
.venv\Scripts\activate.bat   # cmd

# 2. 의존성 확인 (이미 설치됨)
pip install -r requirements.txt

# 3. 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 4101 --reload
# 또는
python app/main.py
```

접속: http://localhost:4101  
Swagger UI: http://localhost:4101/docs  
ReDoc: http://localhost:4101/redoc

---

## 프런트엔드

**요구 사항:** Node.js

```bash
cd frontend

npm run dev      # 개발 서버 (포트 4001, Vite 프록시 /api → localhost:4101)
npm run build    # 프로덕션 빌드 (dist/ 생성)
npm run preview  # 빌드 결과 미리보기
```

접속: http://localhost:4001

> **Vite 프록시:** 개발 중 `/api` 요청은 자동으로 `http://localhost:4101`로 전달됨.

---

## 환경 변수

백엔드 `backend/.env` 파일을 생성한다 (`.env.example` 참조):

```bash
# 인증
SECRET_KEY=랜덤한_강한_키
ACCESS_TOKEN_EXPIRE_MINUTES=20

# MSSQL
MSSQL_HOST=10.100.37.178
MSSQL_PORT=3218
MSSQL_USER=XB01
MSSQL_PASSWORD=패스워드
MSSQL_DB=MFS

# SQLite (로컬 세션)
DATABASE_URL=sqlite:///./mfs.db

# SAP PI
SAP_PI_URL=http://hipop.hhi.co.kr:50000/XISOAPAdapter/MessageServlet
SAP_USER=INFPIUSR
SAP_PASS=패스워드
```

---

## 주요 의존성

### 백엔드 (`backend/requirements.txt`)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `fastapi` | 0.103.2 | 웹 프레임워크 |
| `uvicorn` | 0.23.2 | ASGI 서버 |
| `python-jose[cryptography]` | 3.3.0 | JWT |
| `passlib[bcrypt]` | 1.7.4 | 비밀번호 해시 (pbkdf2_sha256) |
| `pymssql` | 2.2.11 | MSSQL 연결 |
| `sqlalchemy` | 2.0.20 | ORM (SQLite 세션) |
| `pydantic-settings` | 2.0.3 | 환경 설정 |
| `requests` | 2.31.0 | SAP SOAP HTTP |
| `xmltodict` | 0.13.0 | XML → dict 파싱 |
| `python-multipart` | 0.0.6 | form-data 파싱 |

### 프런트엔드 (`frontend/package.json`)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `vue` | 3.3.4 | UI 프레임워크 |
| `vite` | 4.4.5 | 빌드 도구 |
| `pinia` | 2.1.6 | 상태 관리 (초기화만) |
| `vue-router` | 4.2.4 | 라우터 |
| `axios` | 1.5.0 | HTTP 클라이언트 |

---

## 위키 서버 실행

```bash
cd wiki
python -m http.server 4200
```

접속: http://localhost:4200

> **주의:** `wiki/` 디렉토리에서 실행해야 함. 상위 디렉토리에서 실행 시 보안 이슈 있음.
