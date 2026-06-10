---
created: 2026-06-09
phase: init
---

# MFS 하네스 초기화 상태 스냅샷

## 프로젝트 구조

```
E:\AI\mfs\
├── backend/app/
│   ├── main.py              FastAPI 앱 진입점 (port 4101)
│   ├── api/                 라우터 (auth, card_usage, notice, budget, contact, admin)
│   ├── core/                auth, config, mssql, security, soap_client
│   ├── db/                  session(SQLite), mssql_db
│   ├── models/models.py     User, CardUsage, Notice
│   └── schemas/schemas.py   Pydantic 스키마
└── frontend/src/
    ├── views/               7개 뷰 (Login, AdminLogin, Home, CardUsage, Budget, Notice, Contact, Admin)
    └── router/index.js      Vue Router
```

## API 엔드포인트 (prefix: /api/v1)

| 라우터 | 경로 | 비고 |
|--------|------|------|
| auth   | /auth | JWT 로그인 |
| cards  | /cards | 카드 내역 |
| notices| /notices | 공지사항 |
| budget | /budget | 예산 |
| contacts| /contacts | 담당자 연락처 (MSSQL+SAP) |
| admin  | /admin | 관리자 |

## 현재 미커밋 변경사항 (git diff HEAD)

### backend/app/api/contact.py
- SAP 응답 파싱 로직 대폭 강화 (다중 키 탐색, fallback)
- `_first()`, `_split_pipe()` 헬퍼 추가 (pipe-delimited 값 처리)
- 응답 shape 통일: `{DIVISION, TITLE, NAME, TEL, EMAIL, WORK, TASKS[], IS_INTERNAL}`
- TASKS 배열 형식 도입 (name/desc 구조)

### frontend/src/views/ContactView.vue
- 업무 목록을 TASKS 배열 기반으로 전환
- `hasTasks()` 함수 추가
- WORK 구분 태그(work-type-badge) UI 추가
- 소속(DIVISION) 조건부 렌더링
- 업무 없을 때 no-task-row 표시
- CSS 대규모 리팩토링 (인라인 스타일 정리)
