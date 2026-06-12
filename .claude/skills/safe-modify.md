---
name: safe-modify
description: 코드 변경을 사전 영향 분석 → 적용 → 사후 안전성 평가 순으로 안전하게 수행한다. "안전하게 수정", "회귀 위험 없이 변경", "safe modify", "이 변경 안전한가?", "변경 전 체크", "이 패치 적용해도 돼?", "운영 패치 검토", "긴급 핫픽스", "이 수정 GO/NO-GO?", "변경 리뷰" 요청 시 트리거.
model: sonnet
---

# Safe Modify — MFS 안전 변경 워크플로우

## 트리거

- "이거 안전하게 수정해줘"
- "회귀 위험 없이 변경해줘"
- "이 변경 GO/NO-GO 알려줘"
- "변경 전 영향 체크해줘"
- "이 패치 적용해도 돼?"
- "safe modify", "변경 리뷰"

## 실행 방법

`harness-ito:safe-modify` 에이전트를 호출하여 3단계 안전 워크플로우를 실행한다.

### 단계별 처리

1. **사전 분석** (analyze-impact 호출)
   - 변경 대상의 직간접 영향 범위 파악
   - `_workspace/index/call_graph.json` 기반 호출 그래프 확인
   - 위험도 점수 산출

2. **변경 적용** (사용자 확인 후)
   - 영향 범위 보고 후 사용자 승인 요청
   - 코드 수정 실행

3. **사후 검증** (change-safety 에이전트 호출)
   - git diff 기반 회귀 위험 평가
   - GO / HOLD / STOP 권고 산출
   - 영향받는 테스트 목록 표시 (현재 테스트 없음 — 수동 검증 가이드 제공)

## MFS 특화 컨텍스트

### 보안 HIGH 이슈 수정 시 필수 체크리스트

**하드코딩 자격증명 수정 (`config.py`, `mssql_db.py`, `soap_client.py`)**
- [ ] `.env` 파일 생성 (`.gitignore`에 추가 확인)
- [ ] `config.py`의 pydantic-settings에 `env_file=".env"` 설정 추가
- [ ] `MSSQL_SERVER`, `MSSQL_USER`, `MSSQL_PASSWORD`, `MSSQL_DATABASE` 환경변수화
- [ ] `SAP_PI_USER`, `SAP_PI_PASSWORD`, `JWT_SECRET_KEY` 환경변수화
- [ ] 기존 하드코딩 값이 git 히스토리에 남아있는지 확인

**`check_admin()` 수정 (`api/admin.py`)**
- [ ] `get_current_user`에서 반환된 `current_user.is_admin` 검증 로직 추가
- [ ] `Depends(get_current_user)` 반환값에서 `is_admin` 필드 확인
- [ ] 22개 보호 엔드포인트 중 admin 전용 엔드포인트 목록 재확인
- [ ] 변경 후 일반 사용자 토큰으로 `/api/v1/admin/users` 호출 테스트

### 핵심 허브 함수 수정 시 주의

**`get_current_user` (core/auth.py) 수정**
- 영향: 22개 보호 엔드포인트 전체
- 반드시 모든 API 경로 재테스트 필요
- SQLite fallback 로직(`auth.py:get_current_user` 내 가상 User 객체 생성) 유지 여부 확인

**`get_mssql_connection` (core/mssql.py) 수정**
- 영향: 모든 MSSQL 직접 쿼리 (인증, 공지, 연락처, 관리자 CRUD)
- 트랜잭션 패턴 (`conn.commit()` / `conn.rollback()` / `conn.close()`) 유지 필수
- 커넥션 풀 도입 시 `pymssql` 대신 `pyodbc` + SQLAlchemy 연결 풀 검토

**`_call_sap_soap` (core/soap_client.py) 수정**
- 영향: XFI00250~XFI00320 모든 SAP 인터페이스
- SOAP 네임스페이스(`http://hhi.co.kr/FI/XIMOB`), sender service(`P_XIMOB`) 변경 금지
- 타임아웃(30초) 조정 시 SAP 응답 지연 상황 고려

### 트랜잭션 패턴 준수 (admin.py 변경 시)
```python
conn = get_mssql_connection()
try:
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return {"message": "..."}
except Exception as e:
    conn.rollback()
    raise HTTPException(status_code=500, detail=str(e))
finally:
    conn.close()
```
