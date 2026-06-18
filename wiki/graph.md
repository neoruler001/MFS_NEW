# 분석 리포트

## 데드 코드 현황

정적 분석을 통해 발견된 미사용 코드 목록입니다. **자동 제거 금지** — 반드시 수동 검토 후 판단하세요.

| 대상 | 파일 | 신뢰도 | 비고 |
|------|------|--------|------|
| `fetch_mssql_notices()` | db/mssql_db.py | HIGH | 호출처 없음, 레거시 |
| `get_mssql_connection()` | db/mssql_db.py | HIGH | core/mssql.py와 중복 |
| `class CardUsage` | models/models.py | HIGH | SAP로 대체됨 |
| `class Notice` | models/models.py | HIGH | MSSQL로 대체됨 |
| `CardUsageSchema` | schemas/schemas.py | HIGH | import/사용처 없음 |
| `NoticeSchema` | schemas/schemas.py | HIGH | import/사용처 없음 |
| `authenticate_user()` | core/auth.py | MEDIUM | MSSQL 인증으로 대체됨 |
| `check_admin()` | api/admin.py | HIGH | 항상 통과 — 실질 무효 (보안 취약점) |
| `TokenData` | schemas/schemas.py | MEDIUM | 사용처 없음 |

---

## 부분 사용 코드

| 대상 | 비고 |
|------|------|
| `db/session.py (SQLite)` | `get_db()` 의존성이 `get_current_user`에 주입되나 SQLite에서 사용자를 찾지 못하면 가상 User 객체로 우회. 실질적으로 SQLite DB 활용도 매우 낮음. |

---

## 호출 그래프 시각화

함수 호출 관계를 인터랙티브 그래프로 확인할 수 있습니다.

[**호출 그래프 보기 →**](/callgraph.html ':ignore')

- 노드 수: **41개** (백엔드 함수/클래스 기준)
- 엣지 수: **51개**
- 허브 노드: 3개 (in-degree 7 이상)

---

## 의존성 그래프 허브 함수

| 함수 | in-degree | 파일 | 설명 |
|------|-----------|------|------|
| `core.auth.get_current_user` | 12 | core/auth.py | 모든 보호 엔드포인트가 DI로 의존 |
| `core.mssql.get_mssql_connection` | 12 | core/mssql.py | 모든 MSSQL 쿼리의 진입점 |
| `core.soap_client._call_sap_soap` | 7 | core/soap_client.py | 모든 SAP 인터페이스 공통 클라이언트 |

---

## 하네스 평가 리포트 요약

**평가 시각**: 2026-06-11  
**총점**: 92 / 100 — PASS

| 차원 | 점수 | 내용 |
|------|------|------|
| 커버리지 | 25/25 | 6개 라우터·7개 SAP·4개 테이블·3개 허브·보안·데드코드 모두 반영 |
| 정확도 | 20/25 | analyze-impact 엣지 수 기재 오류, 라우트 수 불일치 |
| 실행가능성 | 25/25 | 스킬 트리거 기준 충족, 인덱스 참조 정합성 확인 |
| 컨텍스트 품질 | 22/25 | 운영 배포 구성 미반영 |

### 강점

1. **안티패턴 문서화 수준이 매우 높음** — `check_admin()` 안티패턴이 실제 코드와 완전히 일치하며 수정 코드까지 제시
2. **도메인 특화 컨텍스트** — `sub` vs `target_pernr` 구분, 대리 조회 메커니즘, SAP 파라미터 매핑 등 MFS 특수 비즈니스 로직 명확히 정의
3. **safe-modify.md 체크리스트** — 자격증명 환경변수화, check_admin() 수정 절차를 파일 경로까지 구체적으로 명시

### 개선 필요

| 우선순위 | 대상 | 내용 |
|---------|------|------|
| 1 | analyze-impact.md | "52엣지" → "51엣지" 수정 |
| 2 | CLAUDE.md | "8개 라우트" → "9개 라우트" 수정 |
| 3 | CLAUDE.md | 운영 배포 주의사항 섹션 추가 (선택적) |

---

## 탐지 신뢰도

| 항목 | 신뢰도 | 사유 |
|------|--------|------|
| 스택 탐지 | HIGH | requirements.txt + package.json 직접 확인 |
| 아키텍처 패턴 | HIGH | 소규모 코드베이스, 전체 파일 직독 |
| 의존성 그래프 | HIGH | 17개 Python 파일 전체 분석 |
| 컨벤션 추출 | HIGH | 일관된 패턴, 예외 코드 명확히 식별 |
| DB 스키마 | MEDIUM | SQL 문에서 역추출, 실제 DDL 없음 |
| SAP 응답 구조 | MEDIUM | XFI00310, XFI00290 응답 키 동적 탐색 |
