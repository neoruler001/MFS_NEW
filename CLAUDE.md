# CLAUDE.md — MFS (모바일 법인카드 관리 시스템)

HD현대 그룹 임직원 법인카드 비용처리 및 예산 관리 시스템. FastAPI 백엔드 + Vue 3 프론트엔드 풀스택 구조.

**사용자 호칭:** Neo

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 백엔드 | Python 3.14 + FastAPI (포트 4101) |
| 프런트엔드 | Vue 3.3.4 + Vite 4.4.5 + Pinia 2.1.6 (포트 4001) |
| 내부 DB | SQLite (SQLAlchemy ORM, mfs.db) — 세션용, 실사용 낮음 |
| 운영 DB | MSSQL (10.100.37.178:3218, pymssql 직접 연결) |
| 외부 시스템 | SAP PI (SOAP/XML, http://hipop.hhi.co.kr:50000) |
| 인증 | JWT HS256 (python-jose, 20분 만료) + MSSQL MFS_USERS 인증 |

---

## 아키텍처 구조

```
[Vue 3 SPA] ──axios──> [FastAPI] ──pymssql──> [MSSQL]
                            │
                            └──requests(SOAP)──> [SAP PI]
```

요청 흐름: Vue 컴포넌트 → axios (Authorization: Bearer) → FastAPI 라우터 → Depends(get_current_user) → 서비스(mssql / soap_client) → DB/SAP

---

## 디렉토리 구조

```
mfs_new/
├── backend/
│   └── app/
│       ├── api/            # FastAPI 라우터 (auth, card_usage, notice, budget, contact, admin)
│       ├── core/           # 비즈니스 로직 (auth, security, mssql, soap_client, config)
│       ├── db/             # DB 세션 (session.py — SQLAlchemy, mssql_db.py — 레거시)
│       ├── models/         # SQLAlchemy ORM 모델
│       ├── schemas/        # Pydantic 응답 스키마
│       └── main.py         # FastAPI 앱 진입점
├── frontend/
│   └── src/
│       ├── views/          # 페이지 컴포넌트 (10개)
│       ├── router/         # Vue Router 4 (인증 가드 포함)
│       ├── stores/         # Pinia (초기화만, 실사용 없음)
│       ├── App.vue         # 루트 컴포넌트
│       └── main.js         # 앱 진입점, axios 인터셉터
└── _workspace/             # harness 산출물 (인덱스, 리포트)
```

---

## 핵심 파일 위치

| 레이어 | 파일 경로 | 설명 |
|--------|-----------|------|
| 앱 진입점 | `backend/app/main.py` | FastAPI 인스턴스, CORS, 라우터 등록 |
| 인증 | `backend/app/core/auth.py` | JWT 생성/검증, `get_current_user` DI |
| 보안 | `backend/app/core/security.py` | pbkdf2_sha256 해시/검증 |
| MSSQL 연결 | `backend/app/core/mssql.py` | `get_mssql_connection()` + 쿼리 함수 |
| SAP 클라이언트 | `backend/app/core/soap_client.py` | `_call_sap_soap()` + XFI00250~XFI00320 |
| 환경 설정 | `backend/app/core/config.py` | pydantic-settings 기반 설정 |
| 라우터 - 인증 | `backend/app/api/auth.py` | POST /api/v1/auth/login, /delegate |
| 라우터 - 카드 | `backend/app/api/card_usage.py` | GET/POST /api/v1/cards/* |
| 라우터 - 공지 | `backend/app/api/notice.py` | GET /api/v1/notices/* |
| 라우터 - 예산 | `backend/app/api/budget.py` | GET /api/v1/budget/* |
| 라우터 - 연락처 | `backend/app/api/contact.py` | GET /api/v1/contacts/* |
| 라우터 - 관리자 | `backend/app/api/admin.py` | /api/v1/admin/* (CRUD) |
| Vue 진입점 | `frontend/src/main.js` | axios 기본 설정, 인터셉터 |
| Vue 라우터 | `frontend/src/router/index.js` | 9개 라우트, 인증 가드 |

---

## SAP SOAP 인터페이스 (ZMM_MFS_* 패밀리)

| ID | 설명 | 호출 위치 |
|----|------|----------|
| XFI00250 | 카드 이용내역 / 카드정보 조회 | card_usage.py |
| XFI00260 | 비용처리 (전표 생성) | card_usage.py |
| XFI00270 | 처리취소 (전표 취소) | card_usage.py |
| XFI00280 | 업무목록 조회 | card_usage.py |
| XFI00290 | 예산 조회 | budget.py |
| XFI00310 | 연락처 조회 | contact.py |
| XFI00320 | SAP 공지사항 조회 | notice.py |

모든 SAP 호출은 `soap_client._call_sap_soap()` 를 통해 단일 진입점으로 처리됨.

---

## MSSQL 주요 테이블

| 테이블 | 설명 |
|--------|------|
| `MFS_USERS` | 시스템 사용자 (EMP_NO, KOR_NM, PASSWORD_HASH, IS_ADMIN) |
| `MFS_NOTICES` | 내부 공지사항 (ERDAT, ERZET 기준 정렬) |
| `MFS_CONTACTS` | 내부 연락처 (DIVISION, NAME 기준 정렬) |
| `SUPPORT.DBO.ALL_AMSTM_VIEW` | 인사 정보 뷰 (크로스 DB 조회) |

---

## 핵심 허브 함수 (변경 시 영향 큼)

| 함수 | 파일 | 의존 수 | 주의 |
|------|------|---------|------|
| `get_current_user` | core/auth.py | 12개 엔드포인트 | 모든 보호 엔드포인트 DI |
| `get_mssql_connection` | core/mssql.py | 12개 호출처 | 커넥션 풀 없음, 요청마다 신규 연결 |
| `_call_sap_soap` | core/soap_client.py | 7개 인터페이스 | 동기 블로킹 IO |

---

## 개발 환경 설정

### 백엔드
```bash
cd backend
.venv\Scripts\activate          # Windows 가상환경 활성화
uvicorn app.main:app --host 0.0.0.0 --port 4101 --reload
# 또는
python app/main.py
```

### 프런트엔드
```bash
cd frontend
npm run dev      # 개발 서버 (포트 4001, Vite 프록시 /api → localhost:4101)
npm run build    # 프로덕션 빌드
npm run preview  # 빌드 결과 미리보기
```

---

## 작업 시 주의사항

### 보안 HIGH — 즉시 검토 필요
1. **하드코딩 자격증명**: `backend/app/core/config.py` 및 `backend/app/db/mssql_db.py`에 MSSQL 접속 정보가 소스코드에 직접 기재됨. 수정 시 환경변수(.env)로 이관 필요.
2. **SAP PI 자격증명**: `backend/app/core/soap_client.py`에 INFPIUSR 계정 패스워드 하드코딩. 동일하게 환경변수 이관 필요.
3. **admin API 무방비**: `backend/app/api/admin.py`의 `check_admin()` 함수가 실질적으로 아무 검증도 하지 않음 — 인증된 일반 사용자도 관리자 API 호출 가능. **긴급 보완 필요**.
4. **JWT SECRET_KEY 노출**: `config.py`의 기본값이 `"SuperSecretKeyForDevelopmentOnly"`. 운영 배포 전 반드시 교체.

### 아키텍처 주의
5. `get_mssql_connection()`이 `core/mssql.py`와 `db/mssql_db.py`에 중복 정의됨. `core/mssql.py`가 실사용 버전.
6. SAP SOAP 호출(`requests.post`)이 동기 IO — async FastAPI 이벤트 루프를 블로킹할 수 있음. 고부하 시 `httpx` 비동기 전환 고려.
7. MSSQL 커넥션 풀 없음 — 요청마다 신규 연결 생성. 부하 증가 시 성능 저하 위험.
8. 테스트 코드 없음 (`/tests/` 미존재) — 변경 시 수동 검증 필요.

### 데드 코드 (건드리지 말 것)
- `backend/app/db/mssql_db.py` 전체: 레거시, 미사용
- `backend/app/models/models.py`의 `CardUsage`, `Notice` 클래스: SAP/MSSQL로 대체됨
- `backend/app/core/auth.py`의 `authenticate_user()`: MSSQL 인증으로 대체됨
- `backend/app/schemas/schemas.py`의 `CardUsageSchema`, `NoticeSchema`, `TokenData`: 사용처 없음

---

## 자동 워크플로우

| 상황 | 스킬 |
|------|------|
| API 처리 흐름 추적, Vue→SAP 흐름 | `trace` 스킬 |
| 기능/로직 위치 탐색 | `find-feature` 스킬 |
| 변경 전 영향도 확인 | `analyze-impact` 스킬 |
| 안전한 코드 수정 진행 | `safe-modify` 스킬 |
| 새 기능/API 컨벤션 생성 | `scaffold-feature` 스킬 |
| SQL 쿼리 리뷰 및 점검 | `review-sql` 스킬 |

---

## 변경 이력

| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-05-27 | 초기 하네스 구성 | 전체 | 신규 구축 |
| 2026-06-11 | harness-fin v1 재초기화 — 스택 심층 분석 기반 재구성 | 전체 | 분석 리포트(01_analyzer_report.md) 기반 워크플로우 스킬 + 패턴 파일 추가 |
