# ito-guide — MFS 하네스 사용 설명서

> 이 문서는 MFS(모바일 법인카드 관리 시스템) 프로젝트에 설치된 하네스의 사용 방법을 설명합니다.
> 하네스 구성 요소: 5개 워크플로우 스킬, 1개 도메인 에이전트, 4개 패턴 파일, 6개 인덱스 파일

---

## 1. 스킬 사용법

하네스에는 5개의 워크플로우 스킬이 설치되어 있습니다. 각 스킬은 아래에 나열된 트리거 문장을 입력하면 자동으로 활성화됩니다.

### trace — 처리 흐름 추적

**사용 상황:** Vue 컴포넌트에서 SAP까지 특정 기능의 실행 경로를 파악할 때

| 트리거 예시 |
|-----------|
| "카드 이용내역 조회 흐름 추적해줘" |
| "비용처리 API 어떻게 처리돼?" |
| "Vue에서 SAP까지 어떻게 흘러?" |

내부적으로 `harness-ito:logic-tracer` 에이전트를 호출하며, `_workspace/index/call_graph.json`과 `_workspace/index/external_io.json`을 우선 참조합니다. 로그인/카드조회/비용처리/대리조회 등 4개 주요 흐름은 스킬 파일에 사전 내장되어 있어 즉시 답변이 가능합니다.

---

### analyze-impact — 변경 영향도 분석

**사용 상황:** 코드를 수정하기 전에 어디까지 영향이 미치는지 파악할 때

| 트리거 예시 |
|-----------|
| "get_mssql_connection 바꾸면 어디 영향?" |
| "_call_sap_soap 수정해도 돼?" |
| "이 컬럼 추가하면 어디 영향?" |

`harness-ito:impact-analyzer` 에이전트를 호출합니다. 핵심 허브 함수(`get_current_user` in-degree 12, `get_mssql_connection` in-degree 12, `_call_sap_soap` in-degree 7)에 대한 사전 위험도 평가가 내장되어 있습니다.

---

### safe-modify — 안전 변경 워크플로우

**사용 상황:** 영향 분석 → 변경 적용 → 사후 안전성 검증을 한 번에 수행할 때

| 트리거 예시 |
|-----------|
| "config.py 자격증명 환경변수로 안전하게 수정해줘" |
| "check_admin() 권한 검증 추가해줘, 안전하게" |
| "이 변경 GO/NO-GO 알려줘" |

`harness-ito:safe-modify` 에이전트를 3단계(사전 분석 → 변경 적용 → change-safety 평가)로 실행합니다. 보안 HIGH 이슈 4건 수정 체크리스트가 내장되어 있습니다.

---

### scaffold-feature — 컨벤션 기반 신규 기능 생성

**사용 상황:** 기존 코드 패턴을 그대로 따르는 신규 API 또는 Vue 뷰를 빠르게 생성할 때

| 트리거 예시 |
|-----------|
| "정산 현황 API 추가해줘" |
| "새 SAP 인터페이스 연동 Vue 뷰 만들어줘" |
| "FastAPI 라우터 새로 추가해줘, 패턴대로" |

`harness-ito:scaffold-feature` 에이전트를 호출합니다. `.claude/patterns/*.md` 파일을 로드하여 FastAPI 라우터 → MSSQL DML → SAP SOAP → Vue 컴포넌트 순서로 파일 세트를 생성합니다.

---

### review-sql — SQL 및 SAP 파라미터 리뷰

**사용 상황:** MSSQL 쿼리 성능/보안 점검, SAP 인터페이스 파라미터 검토, DDL 변경 영향 확인 시

| 트리거 예시 |
|-----------|
| "이 쿼리 인덱스 잘 쓰고 있어?" |
| "MFS_USERS INSERT 쿼리 리뷰해줘" |
| "XFI00260 파라미터 점검해줘" |

`harness-ito:sql-reviewer` 에이전트를 호출합니다. 현재 프로젝트의 전체 SQL 목록(8개), pymssql 체크포인트, SAP 인터페이스별 파라미터 정보가 내장되어 있습니다.

---

## 2. 에이전트 직접 호출

### domain-expert — MFS 도메인 전문가

파일 위치: `.claude/agents/domain-expert.md`

도메인 전문 지식이 필요할 때 직접 호출합니다. 법인카드 비용처리 흐름, SAP 인터페이스 상세(XFI00250~XFI00320), MSSQL 테이블 구조, 사번(PERNR) 체계, 인증/인가 구조에 대한 깊은 이해를 기반으로 답변합니다.

#### 호출 방법

```
@domain-expert [질문 내용]
```

#### 사용 시나리오

| 질문 유형 | 예시 |
|----------|------|
| 비즈니스 로직 이해 | "대리 조회에서 sub와 target_pernr가 왜 분리돼?" |
| SAP 인터페이스 설명 | "XFI00260 PE_RESULT 'S'/'E' 의미가 뭐야?" |
| 데이터 구조 질문 | "MFS_USERS 테이블 구조 설명해줘" |
| 아키텍처 판단 | "이 로직을 core/mssql.py에 넣어야 해, api 레이어에 넣어야 해?" |

domain-expert는 에이전트로서 분석 리포트 전체 내용을 시스템 프롬프트에 주입받아 동작하므로, 코드베이스를 다시 탐색하지 않고도 정확한 도메인 답변을 제공합니다.

---

## 3. 패턴 파일 참조

패턴 파일은 `.claude/patterns/` 디렉토리에 위치하며, `scaffold-feature` 스킬이 신규 코드를 생성할 때 컨벤션 기준으로 참조합니다.

> **현재 상태:** 각 패턴 파일은 스켈레톤(뼈대) 상태입니다. "패턴 추출해줘"라고 요청하면 `harness-ito:pattern-extractor`가 실제 코드에서 샘플을 분석하여 내용을 채웁니다.

| 파일 | 용도 | scaffold-feature 연계 |
|------|------|----------------------|
| `api_pattern.md` | FastAPI 라우터 선언, 엔드포인트 함수 시그니처, 에러 처리, async/sync 기준, Pydantic 인라인 스키마 패턴 | 백엔드 라우터 파일(`backend/app/api/{도메인}.py`) 생성 시 참조 |
| `vue_pattern.md` | `<script setup>` 구조, axios 호출, localStorage 접근, 라우터 가드, CSS Custom Properties | Vue 뷰 컴포넌트(`frontend/src/views/{기능}View.vue`) 생성 시 참조 |
| `db_pattern.md` | pymssql 연결/SELECT/DML 패턴, 트랜잭션 처리, `%s` 파라미터 바인딩, 크로스 DB 쿼리 | MSSQL 쿼리 함수(`backend/app/core/mssql.py` 또는 `api/admin.py`) 생성 시 참조 |
| `sap_pattern.md` | SOAP Envelope 구조, 응답 파싱, `call_xfi*()` 함수 패턴, 배열 직렬화(T_DATA) | 신규 SAP 인터페이스 함수(`backend/app/core/soap_client.py`) 생성 시 참조 |

#### scaffold-feature와의 연계 흐름

```
사용자: "정산 현황 조회 API 추가해줘"
  └─> scaffold-feature 스킬 트리거
        └─> .claude/patterns/api_pattern.md 로드   (FastAPI 라우터 패턴)
        └─> .claude/patterns/sap_pattern.md 로드   (SAP SOAP 패턴)
        └─> .claude/patterns/vue_pattern.md 로드   (Vue 컴포넌트 패턴)
              └─> 파일 생성 순서에 따라 5개 파일 생성
                  1. backend/app/api/{도메인}.py
                  2. backend/app/main.py (라우터 등록)
                  3. backend/app/core/soap_client.py (call_xfi* 추가)
                  4. frontend/src/views/{기능}View.vue
                  5. frontend/src/router/index.js (라우트 등록)
```

---

## 4. 인덱스 파일 설명

인덱스 파일은 `_workspace/index/` 디렉토리에 위치하며, 각 스킬과 에이전트가 빠른 분석을 위해 코드베이스를 재탐색하는 대신 우선 참조하는 사전 구축된 메타데이터입니다.

| 파일 | 내용 | 주로 참조하는 스킬 |
|------|------|------------------|
| `call_graph.json` | 함수 호출 그래프 (41노드, 52엣지). `get_current_user`, `get_mssql_connection`, `_call_sap_soap` 등 핵심 허브의 in-degree 정보 포함 | trace, analyze-impact, safe-modify |
| `external_io.json` | SAP SOAP 7건 + MSSQL 직접 쿼리 2개 모듈의 외부 통신 목록. 인터페이스별 URL, 인증 방식, 타임아웃 | trace, analyze-impact |
| `sql_usage.json` | 전체 SQL 8건 목록. 파일, 대상 테이블, 쿼리 타입(SELECT/INSERT/UPDATE/DELETE), 호출 함수 | review-sql, analyze-impact |
| `dead_code.json` | 데드 코드 후보 9건. `db/mssql_db.py`, `models/models.py`의 `CardUsage`·`Notice`, `schemas.py`의 미사용 스키마 등 | analyze-impact, safe-modify |
| `env_branches.json` | 환경 분기 2곳. `session.py`(SQLite 조건), `auth.py:get_current_user`(SQLite fallback) | safe-modify |
| `symbols.json` | 전체 심볼(함수/클래스/변수) 목록. 파일별 정의 위치 | 전체 스킬 공통 |

#### 코드 수정 전 영향 확인 방법

코드를 수정하기 전에 다음 순서로 인덱스를 활용합니다.

```
1. call_graph.json 확인
   → 수정 대상 함수의 in-degree 확인 (호출처 파악)
   → 핵심 허브(in-degree ≥ 7)이면 HIGH 위험 — analyze-impact 스킬 필수 실행

2. external_io.json 확인
   → 수정 대상이 SAP/MSSQL 외부 통신과 연결되어 있는지 확인
   → 연결된 경우 운영 시스템 영향 가능 — safe-modify 스킬 사용 권장

3. dead_code.json 확인
   → 수정 대상이 데드 코드 후보인지 확인
   → 데드 코드이면 안전하게 삭제 또는 무시 가능
```

---

## 5. 실전 시나리오

### 시나리오 1: 신규 SAP 인터페이스 연동 API 추가

**상황:** SAP에 새로운 인터페이스(예: XFI00330 — 월별 정산 현황)가 추가되어, 이를 MFS에 연동하는 신규 엔드포인트와 Vue 화면이 필요한 경우

**사용할 스킬/에이전트:**
- `scaffold-feature` 스킬 (신규 파일 세트 생성)
- `domain-expert` 에이전트 (SAP 인터페이스 패턴 참조)
- `safe-modify` 스킬 (main.py 라우터 등록 변경 시)

**예시 트리거 문장:**

```
"XFI00330 월별 정산 현황 조회 API 추가해줘. SAP SOAP 연동이고 Vue 뷰도 함께 만들어줘."
```

**진행 순서:**

| 단계 | 작업 | 참조 파일 |
|------|------|----------|
| 1 | `backend/app/core/soap_client.py`에 `call_xfi00330()` 추가 | `.claude/patterns/sap_pattern.md` |
| 2 | `backend/app/api/settlement.py` 라우터 생성 | `.claude/patterns/api_pattern.md` |
| 3 | `backend/app/main.py`에 라우터 등록 | — |
| 4 | `frontend/src/views/SettlementView.vue` 생성 | `.claude/patterns/vue_pattern.md` |
| 5 | `frontend/src/router/index.js`에 라우트 추가 | — |

---

### 시나리오 2: 기존 카드 조회 로직 수정 전 영향 확인

**상황:** `core/soap_client.py`의 `_call_sap_soap()` 함수에 요청 로깅 기능을 추가하려는데, 어디까지 영향을 미치는지 확인이 필요한 경우

**사용할 스킬/에이전트:**
- `analyze-impact` 스킬 (영향도 사전 파악)
- `safe-modify` 스킬 (변경 적용 + 사후 검증)

**예시 트리거 문장:**

```
"_call_sap_soap에 요청 로깅 추가하면 어디 영향?"
```

```
"_call_sap_soap 요청 로깅 추가, 안전하게 수정해줘"
```

**확인 포인트:**
- `_call_sap_soap`의 in-degree는 **7** (HIGH 위험)
- XFI00250~XFI00320 전체 SAP 인터페이스에 영향
- 타임아웃 30초 조정 금지, SOAP 네임스페이스 변경 금지
- `_workspace/index/call_graph.json`에서 호출 그래프 확인 가능

---

### 시나리오 3: SQL 쿼리 성능 점검

**상황:** `core/mssql.py`의 `authenticate_mssql_user()` 쿼리가 로그인 응답 속도에 영향을 준다는 의심이 있어, 쿼리를 최적화하기 전에 리뷰가 필요한 경우

**사용할 스킬/에이전트:**
- `review-sql` 스킬 (쿼리 성능/보안/트랜잭션 종합 점검)

**예시 트리거 문장:**

```
"authenticate_mssql_user 쿼리 성능 리뷰해줘"
```

```
"MFS_USERS SELECT 쿼리 인덱스 잘 쓰고 있어?"
```

**리뷰 체크포인트 (review-sql 내장):**

```
성능: WHERE EMP_NO = %s 에서 EMP_NO 인덱스 활용 여부
보안: %s 파라미터 바인딩 사용 여부 (현재 사용 중 — 안전)
커넥션: 요청마다 신규 생성 (커넥션 풀 없음 — 성능 저하 위험)
민감 데이터: PASSWORD_HASH SELECT 범위 최소화 여부
```

---

### 시나리오 4: 화면 오류 추적 (Vue → FastAPI → SAP 흐름)

**상황:** 사용자로부터 "비용처리 버튼을 눌렀는데 오류가 발생한다"는 버그 리포트가 접수된 경우, Vue 컴포넌트부터 SAP 응답까지 전체 흐름을 추적해야 하는 경우

**사용할 스킬/에이전트:**
- `trace` 스킬 (처리 흐름 전체 경로 파악)
- `domain-expert` 에이전트 (SAP PE_RESULT 'E' 의미 확인)
- `analyze-impact` 스킬 (수정 대상 함수 파급 범위 확인 후)

**예시 트리거 문장:**

```
"비용처리 버튼 누르면 어떤 흐름으로 처리돼?"
```

```
"POST /api/v1/cards/process 엔드포인트 흐름 추적해줘"
```

**trace 스킬이 즉시 반환하는 비용처리 흐름:**

```
CardUsageView.vue → POST /api/v1/cards/process
  → api/card_usage.py:process_expenses()
    → core/auth.py:get_current_user()    [JWT 검증, target_pernr 추출]
    → core/soap_client.py:call_xfi00260(t_data)
      → _call_sap_soap("XFI00260", xml_body)
        → requests.post(http://hipop.hhi.co.kr:50000, BasicAuth)
  ← {PE_RESULT, PE_MESSAGE, T_DATA}
  (PE_RESULT='S': 성공 / 'E': SAP 측 오류)
```

오류 원인 후보: JWT 만료(401), SAP 타임아웃(30초), XFI00260 파라미터 누락, 동기 IO 블로킹

---

## 6. 주의사항

하네스 분석 과정에서 발견된 **보안 HIGH 이슈 4건**은 운영 배포 전 반드시 해소해야 합니다.

| # | 위치 | 이슈 | 권장 조치 |
|---|------|------|---------|
| 1 | `backend/app/core/config.py`, `db/mssql_db.py` | MSSQL 접속 자격증명(서버 주소, 사용자, 비밀번호) 소스코드 하드코딩 | `.env` 파일 생성 후 환경변수화. `config.py`에 `env_file=".env"` 추가 |
| 2 | `backend/app/core/soap_client.py` | SAP PI 접속 자격증명(INFPIUSR/패스워드) 소스코드 하드코딩 | `SAP_PI_USER`, `SAP_PI_PASSWORD` 환경변수화 |
| 3 | `backend/app/api/admin.py` | `check_admin()` 함수가 항상 통과 — `/api/v1/admin/*` 12개 엔드포인트 무방비 | `current_user.is_admin` 실질 검증 로직 추가. `safe-modify` 스킬 사용 권장 |
| 4 | `backend/app/core/config.py` | JWT SECRET_KEY 기본값이 "SuperSecretKeyForDevelopmentOnly"로 노출 | 운영용 랜덤 키 생성 후 환경변수화 |

이슈 1~4를 한 번에 해소하려면:

```
"config.py, soap_client.py 하드코딩 자격증명 전부 환경변수로 안전하게 수정해줘"
```

`safe-modify` 스킬이 `.env` 파일 생성부터 git 히스토리 확인까지 체크리스트를 안내합니다.

---

## 7. 하네스 갱신

코드 변경 후 인덱스(`_workspace/index/*.json`)와 패턴 파일(`.claude/patterns/*.md`)이 현실과 어긋나는 경우, 다음 명령으로 하네스를 재초기화합니다.

```
"하네스 다시 초기화해줘"
```

패턴 파일만 최신화하려면:

```
"패턴 추출해줘"
```
