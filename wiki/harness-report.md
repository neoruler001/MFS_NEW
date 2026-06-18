# 하네스 구성 리포트

> harness-init 실행으로 자동 생성된 파일들의 현황입니다.

---

## 생성된 파일 목록

### Core

| 파일 | 경로 | 설명 |
|------|------|------|
| CLAUDE.md | `CLAUDE.md` | 기술 스택, 아키텍처, 파일 위치, 보안 주의사항 |

### 워크플로우 스킬

| 파일 | 경로 | 트리거 |
|------|------|--------|
| trace.md | `.claude/skills/trace.md` | "이 API 어떻게 처리돼?", "흐름 추적" |
| analyze-impact.md | `.claude/skills/analyze-impact.md` | "이거 수정하면 어디 영향?", "영향도 분석" |
| safe-modify.md | `.claude/skills/safe-modify.md` | "안전하게 수정", "GO/NO-GO" |
| scaffold-feature.md | `.claude/skills/scaffold-feature.md` | "[기능] 추가해줘", "새 API 만들어줘" |
| review-sql.md | `.claude/skills/review-sql.md` | "SQL 리뷰해줘", "쿼리 점검" |

### 도메인 에이전트

| 파일 | 경로 | 내용 |
|------|------|------|
| domain-expert.md | `.claude/agents/domain-expert.md` | 법인카드 도메인, 사번 체계, SAP 인터페이스, MSSQL 구조 |

### 코드 패턴

| 파일 | 경로 | 추출 대상 |
|------|------|---------|
| api_pattern.md | `.claude/patterns/api_pattern.md` | FastAPI 라우터, 엔드포인트, 예외 처리 |
| vue_pattern.md | `.claude/patterns/vue_pattern.md` | script setup, axios 호출, 인증 토큰 |
| db_pattern.md | `.claude/patterns/db_pattern.md` | pymssql 연결/쿼리/트랜잭션 패턴 |
| sap_pattern.md | `.claude/patterns/sap_pattern.md` | SOAP Envelope, 응답 파싱, 인터페이스별 특성 |

### 인덱스 파일

| 파일 | 경로 | 내용 |
|------|------|------|
| call_graph.json | `_workspace/index/call_graph.json` | 41노드, 51엣지 호출 그래프 |
| sql_usage.json | `_workspace/index/sql_usage.json` | 원시 SQL 17건 + ORM 쿼리 2건 |
| dead_code.json | `_workspace/index/dead_code.json` | 데드 코드 후보 9건 |
| external_io.json | `_workspace/index/external_io.json` | SAP 7건 + MSSQL 2연결 + SQLite 1건 |
| symbols.json | `_workspace/index/symbols.json` | 백엔드 17모듈, 프런트엔드 11모듈 |
| env_branches.json | `_workspace/index/env_branches.json` | 설정파일 3건, 코드분기 3건 |

---

## 검증 결과 (Validator)

**신뢰도 점수**: 71 / 100

| 항목 | 상태 |
|------|------|
| CLAUDE.md | PASS |
| 스킬 파일 (5개) | PASS |
| 도메인 에이전트 | PASS |
| 패턴 파일 (4개) | PASS (pattern-extractor 실행 완료) |
| 인덱스 파일 | PASS (보안 정보 포함 주의) |

**차감 내역**:

| 항목 | 차감 | 사유 |
|------|------|------|
| 스킬 model 필드 누락 | -10 | 5개 스킬 모두 model 필드 없음 |
| patterns/ 초기 스켈레톤 | -3 | pattern-extractor 실행 전 상태 |
| transactions.json 미생성 | -3 | 단순 패턴으로 리포트에 통합 |
| 인덱스 내 보안 정보 | -3 | env_branches.json 등 자격증명 포함 |
| 인덱스 내 패스워드 평문 | -10 | env_branches.json + external_io.json |

---

## 자동 워크플로우 가이드

Claude Code에서 아래 키워드를 입력하면 해당 스킬이 자동으로 트리거됩니다:

| 상황 | 입력 예시 | 스킬 |
|------|---------|------|
| API 처리 흐름 추적 | "카드 이용내역 API 흐름 보여줘" | trace |
| 기능 위치 탐색 | "비용처리 관련 파일 어디 있어?" | find-feature |
| 변경 전 영향도 확인 | "get_current_user 수정하면 어디 영향?" | analyze-impact |
| 안전한 코드 수정 | "config.py 자격증명 환경변수로 안전하게 수정해줘" | safe-modify |
| 새 기능/API 생성 | "영수증 관리 API 새로 만들어줘" | scaffold-feature |
| SQL 리뷰 | "admin.py의 UPDATE 쿼리 점검해줘" | review-sql |
