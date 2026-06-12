---
name: trace
description: 특정 기능·API·화면의 처리 흐름을 진입점부터 DB/SAP까지 추적한다. "이 API 어떻게 처리돼?", "로그인 흐름 보여줘", "이 화면 버튼 누르면 뭐가 실행돼?", "trace", "흐름 추적", "처리 흐름", "로직 흐름", "이 엔드포인트 어디까지 가?", "Vue에서 SAP까지 어떻게 흘러?", "카드 이용내역 조회 흐름", "비용처리 어떻게 처리돼?" 요청 시 트리거.
model: sonnet
---

# Trace — MFS 처리 흐름 추적

## 트리거

- "이 API 어떻게 처리돼?"
- "로그인 흐름 보여줘"
- "이 화면 버튼 누르면 뭐가 실행돼?"
- "카드 이용내역 조회 흐름 추적해줘"
- "비용처리 어떻게 처리돼?"
- "Vue에서 SAP까지 어떻게 흘러?"
- "이 엔드포인트 추적해줘"
- "trace", "흐름 추적", "처리 흐름", "로직 흐름"

## 실행 방법

`harness-ito:logic-tracer` 에이전트를 호출하여 흐름을 추적한다.

추적 시 다음 인덱스를 우선 활용한다:
- `E:\AI\mfs_new\_workspace\index\call_graph.json` — 함수 호출 그래프
- `E:\AI\mfs_new\_workspace\index\external_io.json` — SAP/MSSQL 외부 통신

## MFS 특화 컨텍스트

### 표준 흐름 경로
```
[Vue 컴포넌트].vue
  └─> axios.get/post('/api/v1/...')
       └─> FastAPI 라우터 (backend/app/api/*.py)
            └─> Depends(get_current_user)  [core/auth.py — JWT 검증]
                 └─> mssql.* 또는 soap_client.*
                      └─> MSSQL (pymssql) 또는 SAP PI (SOAP/XML)
```

### 주요 흐름 사전 파악

**로그인 흐름**
```
LoginView.vue → POST /api/v1/auth/login
  → api/auth.py:login_for_access_token()
    → core/mssql.py:authenticate_mssql_user()  [MFS_USERS SELECT]
    → core/mssql.py:get_mssql_user_info()      [SUPPORT.DBO.ALL_AMSTM_VIEW]
    → core/auth.py:create_access_token()
  ← {access_token, kor_nm, company_nm, is_admin}
```

**카드 이용내역 조회 흐름**
```
CardUsageView.vue → GET /api/v1/cards/usages
  → api/card_usage.py:read_card_usages()
    → core/auth.py:get_current_user()          [JWT 검증, pernr 추출]
    → core/soap_client.py:call_xfi00250()
      → _call_sap_soap("XFI00250", xml_body)
        → requests.post(http://hipop.hhi.co.kr:50000, BasicAuth)
  ← List[카드 이용 내역]
```

**비용처리 흐름**
```
CardUsageView.vue → POST /api/v1/cards/process
  → api/card_usage.py:process_expenses()
    → core/soap_client.py:call_xfi00260(t_data)
  ← {PE_RESULT, PE_MESSAGE, T_DATA}
```

**관리자 대리 조회**
```
HomeView.vue → POST /api/v1/auth/delegate {target_pernr}
  → api/auth.py:delegate_target_user()
    → is_admin 검증 (JWT 페이로드)
    → create_access_token({target_pernr: 대상 사번})
  ← 새 토큰 (이후 카드/예산 조회가 대상 사번으로 실행됨)
```

### 공개 엔드포인트 (인증 불필요)
- `GET /` (루트)
- `GET /health`
- `POST /api/v1/auth/login`

### 모든 기타 엔드포인트
`Depends(get_current_user)` 적용 — 22개 보호 엔드포인트
