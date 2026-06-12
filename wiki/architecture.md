# 아키텍처

## 레이어 구조

```
[프런트엔드] Vue 3 SPA (Vite :4001)
    frontend/src/main.js           — 앱 진입점, axios 설정, 인터셉터
    frontend/src/router/index.js   — Vue Router 4, 9개 라우트, 인증 가드
    frontend/src/App.vue           — 루트 컴포넌트, 뒤로가기 제어
    frontend/src/views/*.vue       — 페이지 컴포넌트 (10개)
         │
         │  axios  (Authorization: Bearer {JWT})
         ▼
[API 레이어] FastAPI (:4101)
    backend/app/main.py            — FastAPI 인스턴스, CORS, 라우터 등록
    backend/app/api/auth.py        — /api/v1/auth/*
    backend/app/api/card_usage.py  — /api/v1/cards/*
    backend/app/api/notice.py      — /api/v1/notices/*
    backend/app/api/budget.py      — /api/v1/budget/*
    backend/app/api/contact.py     — /api/v1/contacts/*
    backend/app/api/admin.py       — /api/v1/admin/*
         │
         │  Depends(get_current_user) — 모든 보호 엔드포인트
         ▼
[서비스/코어 레이어]
    backend/app/core/auth.py       — JWT 생성/검증, 현재 사용자 DI
    backend/app/core/security.py   — pbkdf2_sha256 해시/검증
    backend/app/core/mssql.py      — MSSQL 연결 팩토리 + 쿼리 함수 (실사용)
    backend/app/core/soap_client.py — SAP PI SOAP 클라이언트
    backend/app/core/config.py     — pydantic-settings 기반 설정
         │
         ├── pymssql ──────────────→ [MSSQL :3218]
         │                           MFS_USERS / MFS_NOTICES / MFS_CONTACTS
         │
         └── requests(SOAP) ───────→ [SAP PI :50000]
                                      XFI00250 ~ XFI00320
```

---

## 요청 흐름

### 로그인

```
LoginView.vue
  → POST /api/v1/auth/login  (form-urlencoded: username, password, client_id)
  → api/auth.py: login_for_access_token()
      → mssql.authenticate_mssql_user(emp_no, password)   ← MFS_USERS 인증
      → mssql.get_mssql_user_info(target_pernr)           ← 인사 정보 조회
      → auth.create_access_token({sub, target_pernr, is_admin})
  ← { access_token, token_type, kor_nm, company_nm, is_admin }
  → localStorage 저장 (token, kor_nm, company_nm, is_admin)
```

### 카드 이용내역 조회

```
CardUsageView.vue
  → GET /api/v1/cards/usages?fr_date=&to_date=&pi_status=
      (Authorization: Bearer {token})
  → api/card_usage.py: read_card_usages()
      → auth.get_current_user(token)        ← JWT 검증, target_pernr 추출
      → soap_client.call_xfi00250(params)
          → _call_sap_soap("XFI00250", xml_body)
              → requests.post(SAP_PI_URL, soap_envelope, auth=BasicAuth)
              → ET.fromstring(response) → _parse_xml_to_dict()
  ← List[카드 이용 내역 dict]
```

### 비용처리 (전표 생성)

```
CardUsageView.vue (processExpenses)
  → GET  /api/v1/cards/worklist?bukrs=...   ← 업무목록 조회 (XFI00280)
  → POST /api/v1/cards/process
      { items: [{BUKRS, APPR_DATE, CARD_NUMC, APPR_NUMC, DOCPR, PERNR, SGTXT}] }
  → api/card_usage.py: process_expenses()
      → auth.get_current_user()             ← 처리자 pernr 추출
      → soap_client.call_xfi00260(t_data)   ← SAP 전표 생성
  ← { PE_RESULT, PE_MESSAGE, T_DATA }
```

### 공지사항/연락처 (하이브리드)

```
NoticeView.vue / ContactView.vue
  → GET /api/v1/notices/notices  (or /api/v1/contacts/list)
  → api/notice.py: read_notices()
      ┌→ mssql.get_internal_notices()   ← MFS_NOTICES 조회
      └→ soap_client.call_xfi00320()    ← SAP 공지 조회
      ← 내부 데이터를 앞에 배치하여 병합 반환
```

### 관리자 대리 조회

```
HomeView.vue (searchByPernr)
  → POST /api/v1/auth/delegate  { target_pernr: "BP26745" }
      (관리자 토큰 필요)
  → api/auth.py: delegate_target_user()
      → is_admin 검증
      → mssql.get_mssql_user_info(target_pernr)
      → create_access_token({sub: admin_emp, target_pernr: target, is_admin: true})
  ← 새 토큰 (target_pernr가 대상 사번으로 설정됨)
  → 이후 카드/예산 조회 시 대상 사번으로 SAP 호출
```

---

## 데이터 접근 패턴

| 데이터 | 접근 방식 | 저장소 |
|--------|----------|--------|
| 인증 (로그인) | pymssql raw SQL | MSSQL `MFS_USERS` |
| 인사 정보 (사번→이름) | pymssql raw SQL | MSSQL `SUPPORT.DBO.ALL_AMSTM_VIEW` |
| 카드 이용내역 | SAP SOAP XFI00250 | SAP ERP |
| 비용처리/취소 | SAP SOAP XFI00260/270 | SAP ERP |
| 업무목록 | SAP SOAP XFI00280 | SAP ERP |
| 예산 | SAP SOAP XFI00290 | SAP ERP |
| 연락처 | pymssql + SAP SOAP XFI00310 | MSSQL + SAP ERP |
| 공지사항 | pymssql + SAP SOAP XFI00320 | MSSQL + SAP ERP |
| 관리자 CRUD | pymssql raw SQL | MSSQL |
| JWT 세션 | SQLAlchemy (SQLite) | `mfs.db` (실질적 활용 낮음) |

---

## 의존성 허브

```
get_current_user (in-degree: 12)
  ← read_card_usages, process_expenses, cancel_expenses
  ← get_worklist, get_card_info
  ← get_budget
  ← read_notices, read_contacts
  ← list_admin_*, create/update/delete_*

get_mssql_connection (in-degree: 12)
  ← authenticate_mssql_user, get_mssql_user_info
  ← get_internal_notices, get_internal_contacts
  ← 모든 admin.py DML 함수

_call_sap_soap (in-degree: 7)
  ← call_xfi00250~xfi00320 전 인터페이스
```

---

## Vue 라우트 구성

| 경로 | 컴포넌트 | 인증 필요 |
|------|---------|---------|
| `/login` | `LoginView.vue` | ✗ |
| `/` | `HomeView.vue` | ✓ |
| `/card` | `CardUsageView.vue` | ✓ |
| `/budget` | `BudgetView.vue` | ✓ |
| `/notice` | `NoticeView.vue` | ✓ |
| `/contact` | `ContactView.vue` | ✓ |
| `/mypage` | `MyPageView.vue` | ✓ |
| `/admin` | `AdminView.vue` | ✓ (관리자) |
| `/admin/login` | `AdminLoginView.vue` | ✗ |
