---
name: analyze-impact
description: 변경 대상(파일/함수/클래스/SQL/엔드포인트/DB 컬럼)의 직간접 영향과 위험도를 분석한다. "이거 수정하면 어디 영향?", "이 함수 건드려도 돼?", "영향도 분석", "이 SQL 바꾸면 어디 영향?", "이 컬럼 추가했을 때 영향", "impact analysis", "이 API 변경 영향", "어디서 쓰이고 있어?", "이 메서드 호출처", "이 함수 수정해도 돼?" 요청 시 트리거.
model: sonnet
---

# Analyze Impact — MFS 변경 영향도 분석

## 트리거

- "이거 수정하면 어디 영향?"
- "이 함수 건드려도 돼?"
- "영향도 분석해줘"
- "get_current_user 수정해도 돼?"
- "get_mssql_connection 바꾸면 어디 영향?"
- "_call_sap_soap 수정하면?"
- "이 SQL 바꿨을 때 영향"
- "이 컬럼 추가하면 어디 영향?"
- "impact analysis", "어디서 쓰이고 있어?", "호출처 알려줘"

## 실행 방법

`harness-ito:impact-analyzer` 에이전트를 호출하여 직간접 영향과 위험도를 분석한다.

분석 시 다음 인덱스를 우선 활용한다:
- `E:\AI\mfs_new\_workspace\index\call_graph.json` — 함수 호출 그래프 (41노드, 51엣지)
- `E:\AI\mfs_new\_workspace\index\external_io.json` — 외부 통신 목록
- `E:\AI\mfs_new\_workspace\index\sql_usage.json` — SQL 사용 현황
- `E:\AI\mfs_new\_workspace\index\dead_code.json` — 데드 코드 목록

## MFS 특화 컨텍스트

### 핵심 허브 함수 — 변경 시 파급 범위가 매우 큼

| 함수 | 파일 | in-degree | 영향 범위 |
|------|------|-----------|----------|
| `get_current_user` | core/auth.py | 12 | 22개 보호 엔드포인트 전체 |
| `get_mssql_connection` | core/mssql.py | 12 | 모든 MSSQL 직접 쿼리 |
| `_call_sap_soap` | core/soap_client.py | 7 | XFI00250~XFI00320 전체 |
| `create_access_token` | core/auth.py | 2 | 로그인, 대리 조회 |
| `verify_password` | core/security.py | 2 | 인증, 비밀번호 변경 |

### SAP 인터페이스 의존 관계

| 인터페이스 | 호출 엔드포인트 | 영향 화면 |
|-----------|--------------|---------|
| XFI00250 | read_card_usages, get_card_info | CardUsageView |
| XFI00260 | process_expenses | CardUsageView (비용처리) |
| XFI00270 | cancel_expenses | CardUsageView (취소) |
| XFI00280 | get_work_list | CardUsageView (업무목록 팝업) |
| XFI00290 | read_budget | BudgetView |
| XFI00310 | read_contacts | ContactView |
| XFI00320 | read_notices | NoticeView |

### 변경 위험도 사전 평가

**위험도 HIGH (변경 전 반드시 analyze-impact 실행)**
- `core/auth.py` 내 `get_current_user`, `create_access_token`
- `core/mssql.py` 내 `get_mssql_connection`, `authenticate_mssql_user`
- `core/soap_client.py` 내 `_call_sap_soap`
- `backend/app/api/auth.py` 전체

**위험도 MEDIUM**
- 각 `call_xfi*` 함수 (1개 엔드포인트에만 영향)
- `admin.py`의 DML 함수 (트랜잭션 처리 패턴 준수 필요)

**위험도 LOW (변경 안전)**
- `db/mssql_db.py` — 레거시, 실사용 없음
- `models/models.py`의 `CardUsage`, `Notice` 클래스 — 데드 코드
- `schemas/schemas.py`의 `CardUsageSchema`, `NoticeSchema` — 미사용
