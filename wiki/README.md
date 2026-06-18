# MFS — 모바일 법인카드 관리 시스템

> HD현대 그룹 임직원의 법인카드 비용처리 및 예산 관리를 위한 시스템입니다.

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 시스템명 | MFS (Mobile Finance System) |
| 도메인 | HD현대 그룹 법인카드 비용처리 및 예산 관리 |
| 백엔드 | Python 3.14 + FastAPI (포트 4101) |
| 프런트엔드 | Vue 3.3.4 + Vite 4.4.5 (포트 4001) |
| 운영 DB | MSSQL (pymssql 직접 연결) |
| 외부 시스템 | SAP PI (SOAP/XML) |
| 인증 | JWT HS256 (20분 만료) + MSSQL 인증 |

---

## 아키텍처 한눈에 보기

```
[Vue 3 SPA] ──axios──> [FastAPI] ──pymssql──> [MSSQL]
                            │
                            └──SOAP/HTTP──> [SAP PI]
```

요청 흐름: `Vue 컴포넌트 → axios (Bearer 토큰) → FastAPI 라우터 → Depends(get_current_user) → 서비스 레이어 → DB / SAP`

---

## 빠른 탐색

| 내용 | 링크 |
|------|------|
| 아키텍처 및 디렉토리 구조 | [아키텍처](/architecture) |
| 개발 환경 설정 (실행 방법) | [설정 가이드](/setup) |
| 데이터베이스 테이블 및 SQL 패턴 | [데이터베이스](/database) |
| SAP SOAP 인터페이스 7종 | [SAP 인터페이스](/sap) |
| 보안 이슈 목록 (HIGH 포함) | [보안](/security) |
| 코드 컨벤션 (API / DB / Vue / SAP) | [컨벤션 가이드](/conventions) |
| 함수 호출 그래프 (시각화) | [호출 그래프](/callgraph.html ':ignore') |
| 데드 코드 및 분석 리포트 | [분석 리포트](/graph) |

---

## SAP 인터페이스 요약

| ID | 설명 | 호출 엔드포인트 |
|----|------|--------------|
| XFI00250 | 카드 이용내역 / 카드정보 조회 | GET /api/v1/cards/usages |
| XFI00260 | 비용처리 (전표 생성) | POST /api/v1/cards/process |
| XFI00270 | 처리취소 (전표 취소) | POST /api/v1/cards/cancel |
| XFI00280 | 업무목록 조회 | GET /api/v1/cards/worklist |
| XFI00290 | 예산 조회 | GET /api/v1/budget/budget |
| XFI00310 | 연락처 조회 | GET /api/v1/contacts/list |
| XFI00320 | SAP 공지사항 조회 | GET /api/v1/notices/notices |

---

## 핵심 허브 함수

변경 시 전체 시스템에 영향을 주는 함수들입니다.

| 함수 | in-degree | 설명 |
|------|-----------|------|
| `core.auth.get_current_user` | 12 | 모든 보호 엔드포인트가 DI로 의존 |
| `core.mssql.get_mssql_connection` | 12 | 모든 MSSQL 직접 쿼리의 진입점 |
| `core.soap_client._call_sap_soap` | 7 | 모든 SAP 인터페이스 공통 HTTP 클라이언트 |

---

## 보안 주의사항 (HIGH)

> 운영 배포 전 반드시 해결해야 할 항목입니다.

1. **하드코딩 자격증명** — `config.py`, `soap_client.py`에 DB/SAP 접속 정보 평문 기재
2. **admin API 무방비** — `check_admin()` 함수가 실질적 검증 없이 통과
3. **JWT SECRET_KEY 노출** — 기본값이 `"SuperSecretKeyForDevelopmentOnly"`
4. **CORS 전체 허용** — `allow_origins=["*"]` 운영 배포 시 제한 필요

자세한 내용은 [보안 이슈](/security) 페이지를 참고하세요.

---

## 하네스 평가 결과

| 항목 | 결과 |
|------|------|
| 전체 점수 | **92 / 100 — PASS** |
| 커버리지 | 25/25 |
| 정확도 | 20/25 |
| 실행가능성 | 25/25 |
| 컨텍스트 품질 | 22/25 |

*분석 시각: 2026-06-11*
