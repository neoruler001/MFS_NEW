# 아키텍처

## 기술 스택

| 항목 | 내용 |
|------|------|
| 백엔드 언어 | Python 3.14 |
| 백엔드 프레임워크 | FastAPI |
| 프런트엔드 | Vue 3.3.4 (Composition API, `<script setup>`) |
| 빌드 도구 | Vite 4.4.5 |
| 상태 관리 | Pinia 2.1.6 (초기화만, 실사용 없음) |
| HTTP 클라이언트 (프런트) | Axios 1.5.0 |
| 내부 DB (로컬) | SQLite (SQLAlchemy ORM, mfs.db) — 세션용, 실사용 낮음 |
| 운영 DB | MSSQL (10.100.37.178:3218, pymssql 직접 연결) |
| 외부 시스템 | SAP PI (SOAP/XML) |
| 인증 방식 | JWT HS256 (python-jose, 20분 만료) + MSSQL MFS_USERS 인증 |
| 비밀번호 해시 | pbkdf2_sha256 (passlib) |
| 백엔드 포트 | 4101 |
| 프런트엔드 포트 | 4001 |

---

## 전체 아키텍처

```
┌──────────────────────────────────────────────────────────┐
│                  Vue 3 SPA (Vite, 포트 4001)             │
│  frontend/src/views/*.vue  (10개 페이지 컴포넌트)          │
│  frontend/src/router/index.js  (9개 라우트, 인증 가드)     │
│  frontend/src/main.js  (axios 설정, 401 인터셉터)          │
└─────────────────────┬────────────────────────────────────┘
                      │ axios (Authorization: Bearer {JWT})
                      │ /api/* → proxy → localhost:4101
                      ▼
┌──────────────────────────────────────────────────────────┐
│              FastAPI 서버 (포트 4101)                      │
│  backend/app/main.py  (앱 인스턴스, CORS, 라우터 등록)     │
│                                                          │
│  ┌──────────┐ ┌───────────┐ ┌────────┐ ┌──────────────┐ │
│  │ /auth    │ │ /cards    │ │/notices│ │ /admin       │ │
│  │ /budget  │ │ /contacts │ └────────┘ └──────────────┘ │
│  └──────────┘ └───────────┘                             │
│                                                          │
│  core/auth.py  ─── JWT 생성·검증 (get_current_user DI)   │
│  core/mssql.py ─── MSSQL 연결 팩토리 + 쿼리 함수         │
│  core/soap_client.py ── SAP SOAP 클라이언트              │
│  core/security.py ─── pbkdf2_sha256 해시/검증           │
│  core/config.py ─── pydantic-settings 환경 설정          │
└──────────┬──────────────────────┬────────────────────────┘
           │ pymssql              │ requests (SOAP/XML)
           ▼                      ▼
┌─────────────────┐   ┌──────────────────────────────────┐
│  MSSQL DB       │   │  SAP PI (Process Integration)    │
│  MFS_USERS      │   │  http://hipop.hhi.co.kr:50000    │
│  MFS_NOTICES    │   │  XFI00250 ~ XFI00320 (7종)       │
│  MFS_CONTACTS   │   └──────────────────────────────────┘
│  SUPPORT.DBO.*  │
└─────────────────┘
```

---

## 디렉토리 구조

```
mfs_new/
├── backend/
│   └── app/
│       ├── api/            # FastAPI 라우터
│       │   ├── auth.py         — POST /api/v1/auth/login, /delegate
│       │   ├── card_usage.py   — GET/POST /api/v1/cards/*
│       │   ├── notice.py       — GET /api/v1/notices/*
│       │   ├── budget.py       — GET /api/v1/budget/*
│       │   ├── contact.py      — GET /api/v1/contacts/*
│       │   └── admin.py        — /api/v1/admin/* (CRUD)
│       ├── core/           # 비즈니스 로직
│       │   ├── auth.py         — JWT 생성/검증, get_current_user DI
│       │   ├── security.py     — pbkdf2_sha256 해시/검증
│       │   ├── mssql.py        — MSSQL 연결 팩토리 + 쿼리 함수 ★실사용
│       │   ├── soap_client.py  — SAP PI SOAP 클라이언트 (7개 인터페이스)
│       │   └── config.py       — pydantic-settings 기반 설정
│       ├── db/             # DB 세션
│       │   ├── session.py      — SQLAlchemy 엔진/세션 (SQLite)
│       │   └── mssql_db.py     — MSSQL 연결 (레거시, 미사용)
│       ├── models/
│       │   └── models.py       — SQLAlchemy ORM (User, CardUsage, Notice)
│       ├── schemas/
│       │   └── schemas.py      — Pydantic 응답 스키마
│       └── main.py         # FastAPI 앱 진입점
├── frontend/
│   └── src/
│       ├── views/          # 페이지 컴포넌트 (10개)
│       │   ├── LoginView.vue
│       │   ├── AdminLoginView.vue
│       │   ├── HomeView.vue
│       │   ├── CardUsageView.vue
│       │   ├── NoticeView.vue
│       │   ├── BudgetView.vue
│       │   ├── ContactView.vue
│       │   ├── AdminView.vue
│       │   ├── SettingsView.vue
│       │   └── ProfileView.vue
│       ├── router/
│       │   └── index.js    — Vue Router 4 (9개 라우트, 인증 가드)
│       ├── stores/         — Pinia (초기화만, 실사용 없음)
│       ├── App.vue         — 루트 컴포넌트, 뒤로가기 제어
│       └── main.js         — 앱 진입점, axios 인터셉터
├── _workspace/             # harness 분석 산출물
│   ├── index/              — JSON 인덱스 파일
│   │   ├── call_graph.json
│   │   ├── sql_usage.json
│   │   ├── dead_code.json
│   │   ├── external_io.json
│   │   ├── symbols.json
│   │   └── env_branches.json
│   ├── 01_analyzer_report.md
│   ├── 02_writer_files.md
│   ├── 03_validator_report.md
│   └── 06_eval_report.md
└── .claude/
    ├── skills/             — 워크플로우 스킬 (trace, analyze-impact 등)
    ├── patterns/           — 코드 패턴 가이드
    └── agents/             — 도메인 에이전트
```

---

## 요청 흐름 (플로우)

### 1. 로그인 흐름

```
LoginView.vue
  → POST /api/v1/auth/login
    (form-urlencoded: username, password, client_id)
  → api/auth.py: login_for_access_token()
      → mssql.authenticate_mssql_user(emp_no, password)  [MFS_USERS 조회]
      → mssql.get_mssql_user_info(target_pernr)          [인사 정보 조회]
      → auth.create_access_token({sub, target_pernr, is_admin})
  ← {access_token, token_type, kor_nm, company_nm, is_admin}
  → localStorage 저장 (token, kor_nm, company_nm, is_admin)
```

### 2. 카드 이용내역 조회 흐름

```
CardUsageView.vue
  → GET /api/v1/cards/usages?fr_date=&to_date=&pi_status=
    (Authorization: Bearer {token})
  → api/card_usage.py: read_card_usages()
      → auth.get_current_user(token)       [JWT 검증, target_pernr 추출]
      → soap_client.call_xfi00250(params)
          → _call_sap_soap("XFI00250", xml_body)
              → requests.post(SAP_PI_URL, soap_envelope)
              → ET.fromstring(response) → _parse_xml_to_dict()
  ← List[카드 이용 내역 딕셔너리]
```

### 3. 비용처리 흐름

```
CardUsageView.vue (processExpenses)
  → GET /api/v1/cards/worklist?bukrs=   [업무 목록 → XFI00280]
  → POST /api/v1/cards/process
    { items: [{BUKRS, APPR_DATE, CARD_NUMC, APPR_NUMC, DOCPR, PERNR, SGTXT}] }
  → api/card_usage.py: process_expenses()
      → auth.get_current_user()
      → soap_client.call_xfi00260(t_data)  [SAP 전표 생성]
  ← {PE_RESULT, PE_MESSAGE, T_DATA}
```

### 4. 공지사항 (하이브리드) 흐름

```
NoticeView.vue
  → GET /api/v1/notices/notices
  → api/notice.py: read_notices()
      ┌→ mssql.get_internal_notices()   [MFS_NOTICES — 내부 공지]
      └→ soap_client.call_xfi00320()    [SAP 공지]
      ← 내부 데이터를 앞에 배치하여 병합 반환
```

### 5. 관리자 대리 조회 흐름

```
HomeView.vue (searchByPernr)
  → POST /api/v1/auth/delegate  { target_pernr: "BP26745" }
    (관리자 토큰 필요)
  → api/auth.py: delegate_target_user()
      → is_admin 검증
      → mssql.get_mssql_user_info(target_pernr)
      → create_access_token({sub: admin_emp, target_pernr: target})
  ← 새 토큰 (target_pernr가 대상 사번으로 설정됨)
  → 이후 카드/예산 조회 시 대상 사번으로 SAP 호출
```

---

## 인증/인가 구조

### JWT 토큰 페이로드

```json
{
  "sub": "BP12345",          // 실제 로그인 사번 (관리자)
  "target_pernr": "BP67890", // SAP/DB 조회에 사용할 사번 (대리 조회 시 다름)
  "is_admin": true,
  "exp": 1748000000
}
```

### 보호 엔드포인트

- `Depends(get_current_user)` 적용: **22개** 엔드포인트
- 공개 엔드포인트: `GET /`, `GET /health`, `POST /api/v1/auth/login`

### 환경 분기

- 단일 환경 운영 (dev/stg/prod 분리 없음)
- CORS: `allow_origins=["*"]` 전체 허용 (개발 편의 — 운영 시 제한 필요)

---

## 비동기 처리 현황

| 엔드포인트 | async/sync | 비고 |
|-----------|-----------|------|
| login_for_access_token | `async def` | OAuth2 폼 처리 |
| delegate_target_user | `async def` | 토큰 재발급 |
| get_current_user | `async def` | JWT 검증 |
| read_card_usages | `def` (동기) | SAP SOAP 동기 I/O |
| process_expenses | `def` (동기) | SAP SOAP 동기 I/O |
| read_budget | `def` (동기) | SAP SOAP 동기 I/O |

> ⚠️ SAP SOAP 호출(`requests.post`)이 동기 IO로 FastAPI 이벤트 루프를 블로킹할 수 있습니다. 고부하 시 `httpx` 비동기 전환을 고려하세요.
