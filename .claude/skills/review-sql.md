---
name: review-sql
description: MFS MSSQL 쿼리와 SAP 인터페이스 파라미터를 리뷰한다. "SQL 리뷰해줘", "이 쿼리 점검", "SQL review", "N+1 확인", "이 쿼리 성능", "인덱스 잘 쓰고 있어?", "이 SQL 안전한가?", "DDL 영향 분석", "이 컬럼 추가해도 돼?", "쿼리 검토", "운영 SQL 검토" 요청 시 트리거.
model: sonnet
---

# Review SQL — MFS SQL 리뷰

## 트리거

- "이 SQL 리뷰해줘"
- "이 쿼리 점검해줘"
- "N+1 확인해줘"
- "이 쿼리 성능 어때?"
- "인덱스 잘 쓰고 있어?"
- "이 컬럼 추가해도 돼?"
- "SQL review", "쿼리 검토", "운영 SQL 검토"

## 실행 방법

`harness-ito:sql-reviewer` 에이전트를 호출하여 SQL 텍스트 또는 변경 diff를 리뷰한다.

다음 인덱스를 우선 활용한다:
- `E:\AI\mfs_new\_workspace\index\sql_usage.json` — 전체 SQL 목록 + 호출처
- `E:\AI\mfs_new\_workspace\index\call_graph.json` — SQL 함수 호출 그래프

## MFS 특화 컨텍스트

### 현재 SQL 목록 (sql_usage.json 기반)

| SQL ID | 파일 | 대상 테이블 | 타입 | 호출처 |
|--------|------|------------|------|--------|
| mssql.authenticate_mssql_user | core/mssql.py | MFS_USERS | SELECT | login_for_access_token |
| mssql.get_mssql_user_info | core/mssql.py | SUPPORT.DBO.ALL_AMSTM_VIEW | SELECT | login, delegate |
| mssql.get_internal_notices | core/mssql.py | MFS_NOTICES | SELECT | read_notices |
| mssql.get_internal_contacts | core/mssql.py | MFS_CONTACTS | SELECT | read_contacts |
| admin.list_users | api/admin.py | MFS_USERS | SELECT | list_admin_users |
| admin.create_user | api/admin.py | MFS_USERS | INSERT | create_admin_user |
| admin.update_user | api/admin.py | MFS_USERS | UPDATE | update_admin_user |
| admin.delete_user | api/admin.py | MFS_USERS | DELETE | delete_admin_user |

### MSSQL pymssql 쿼리 패턴 체크포인트

**파라미터 바인딩 (인젝션 방지)**
- 올바른 패턴: `cursor.execute("SELECT * FROM T WHERE COL = %s", (value,))`
- 금지 패턴: f-string 직접 삽입 (`f"... WHERE COL = '{value}'"`)
- 현재 프로젝트: `%s` 바인딩 사용 중 — SQL 인젝션 방지됨

**커넥션 관리**
- 현재: 요청마다 `pymssql.connect()` 신규 생성 (커넥션 풀 없음)
- SELECT 쿼리: `cursor(as_dict=True)` 사용 권장
- DML 쿼리: 반드시 `conn.commit()` / `conn.rollback()` / `conn.close()` 3단계

**크로스 DB 쿼리 주의**
- `SUPPORT.DBO.ALL_AMSTM_VIEW` — 외부 DB 뷰 조회
- 해당 뷰의 `HLD_OFFI_GBN <> '3'` 필터 조건 변경 시 인사 데이터 범위 변경됨

### SAP 인터페이스 파라미터 검토

**XFI00250 (카드 이용내역)** 입력 파라미터:
- `PI_CARD_NUMC`, `PI_FR_DATE`, `PI_TO_DATE`, `PI_STATUS`
- `PI_PERNR_O` (원 사번), `PI_PERNR_R` (조회 사번), `PI_CALLSYS`

**XFI00260 (비용처리)** T_DATA 항목:
- `BUKRS`, `BUDAT`, `CARD_NUMC`, `APPR_DATE`, `APPR_NUMC`
- `CANC_FLAG`, `SEQN_NUMC`, `DOCPR`, `PERNR_O`, `PERNR_R`, `SGTXT`

**XFI00280 (업무목록)** 출력:
- `PE_RESULT`, `PE_MESSAGE`, `TE_TEMPLATE`, `TE_SGTXT`, `TE_DOCPR_SGTXT`

**XFI00290 (예산)** 주의: 응답 키 구조가 동적 — `_parse_xml_to_dict()` 의존

### 리뷰 체크리스트

**성능**
- [ ] WHERE 절에 인덱스 컬럼 사용 여부 (MFS_USERS.EMP_NO 등)
- [ ] `SELECT *` 사용 여부 (필요 컬럼만 명시 권장)
- [ ] N+1 패턴 여부 (루프 내 쿼리 실행)
- [ ] 대용량 결과셋 페이징 처리 여부

**보안**
- [ ] 파라미터 바인딩 (`%s`) 사용 여부
- [ ] 민감 데이터(비밀번호 해시 등) 불필요한 SELECT 여부

**트랜잭션**
- [ ] DML 후 `conn.commit()` 호출 여부
- [ ] 예외 발생 시 `conn.rollback()` 처리 여부
- [ ] `conn.close()` finally 블록 처리 여부

**스키마 영향**
- [ ] DDL 변경이 기존 쿼리와 호환 여부
- [ ] 테이블 DDL 파일 없음 — 실제 MSSQL 서버 컬럼 직접 확인 필요
