# 개발 환경 설정

## 사전 요구사항

| 항목 | 버전 |
|------|------|
| Python | 3.14 이상 |
| Node.js | 18 이상 (LTS 권장) |
| npm | 9 이상 |
| MSSQL 접속 권한 | 운영팀 확인 |
| SAP PI 접속 가능 여부 | 사내 네트워크 필요 |

---

## 백엔드 설정

### 1. 가상환경 활성화

```bash
cd backend
# Windows
.venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

`backend/.env` 파일을 생성하여 설정합니다 (`.gitignore`에 포함됨):

```ini
# JWT
SECRET_KEY=your-production-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=20

# MSSQL
MSSQL_HOST=10.100.37.178
MSSQL_PORT=3218
MSSQL_USER=XB01
MSSQL_PASSWORD=your-db-password
MSSQL_DB=

# SAP PI
SAP_PI_URL=http://hipop.hhi.co.kr:50000/XISOAPAdapter/MessageServlet
SAP_USER=INFPIUSR
SAP_PASS=your-sap-password
```

> ⚠️ `.env` 파일을 Git에 커밋하지 마세요. 현재 `config.py`에 자격증명이 하드코딩되어 있으나 환경변수 이관이 필요합니다. ([보안 이슈](/security) 참고)

### 4. 서버 실행

```bash
# 개발 서버 (핫리로드)
uvicorn app.main:app --host 0.0.0.0 --port 4101 --reload

# 또는 직접 실행
python app/main.py
```

서버 확인: http://localhost:4101

API 문서 (Swagger UI): http://localhost:4101/docs

---

## 프런트엔드 설정

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

Vite 개발 서버가 http://localhost:4001 에서 실행됩니다.

`/api/*` 요청은 자동으로 `localhost:4101`로 프록시됩니다 (`vite.config.js` 설정).

### 3. 프로덕션 빌드

```bash
npm run build    # dist/ 폴더에 빌드 결과 생성
npm run preview  # 빌드 결과 로컬 미리보기
```

---

## 로컬 서버 실행 순서

```bash
# 터미널 1 — 백엔드
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 4101 --reload

# 터미널 2 — 프런트엔드
cd frontend
npm run dev
```

브라우저에서 http://localhost:4001 접속

---

## 주요 라우트 (프런트엔드)

| 경로 | 컴포넌트 | 인증 필요 |
|------|---------|---------|
| `/login` | LoginView.vue | 불필요 |
| `/admin-login` | AdminLoginView.vue | 불필요 |
| `/` | HomeView.vue | 필요 |
| `/card-usage` | CardUsageView.vue | 필요 |
| `/notice` | NoticeView.vue | 필요 |
| `/budget` | BudgetView.vue | 필요 |
| `/contact` | ContactView.vue | 필요 |
| `/admin` | AdminView.vue | 필요 |
| `/settings` | SettingsView.vue | 필요 |

---

## API 엔드포인트 확인

백엔드가 실행 중인 경우 아래 URL에서 자동 생성 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:4101/docs
- **ReDoc**: http://localhost:4101/redoc
- **헬스체크**: http://localhost:4101/health

---

## 데이터베이스 초기화

SQLite (`mfs.db`) 는 FastAPI 앱 최초 실행 시 자동 생성됩니다.  
MSSQL 테이블(`MFS_USERS`, `MFS_NOTICES`, `MFS_CONTACTS`)은 사전에 운영 DB에 존재해야 합니다.

> 최초 관리자 계정이 없으면 로그인이 불가합니다. 운영팀에 최초 계정 등록을 요청하거나 직접 MSSQL에 INSERT합니다.

---

## 빌드 파이프라인

현재 CI/CD 파이프라인은 미구성 상태입니다. 수동 배포 절차:

1. 프런트엔드 빌드: `npm run build` → `dist/` 생성
2. 백엔드 서버 재시작
3. `dist/` 를 nginx 또는 정적 파일 서버로 서빙

> 운영 배포 시 nginx 리버스 프록시 설정 및 SSL 적용이 필요합니다.
