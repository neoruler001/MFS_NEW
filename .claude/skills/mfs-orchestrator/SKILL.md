---
name: MFS 오케스트레이터
description: >
  MFS(모바일 법인카드 관리 시스템) 관련 기능 구현, 수정, 버그 수정, 새 API/뷰 추가, 기능 개선 등
  모든 개발 작업 요청 시 반드시 이 스킬을 사용한다.
  "카드 내역", "예산", "공지", "연락처", "관리자", "로그인", "인증", "백엔드", "프론트엔드",
  "FastAPI", "Vue", "API 추가", "뷰 만들어", "기능 구현", "다시 실행", "재실행", "수정해줘",
  "보완해줘", "이전 결과 기반으로" 등의 표현이 포함된 요청에 적용한다.
  단순 질문이나 개념 설명 요청에는 적용하지 않는다.
---

# MFS 오케스트레이터 스킬

MFS 프로젝트의 개발 작업을 에이전트 팀으로 조율하는 스킬이다.
mfs-lead 에이전트가 리더로서 팀을 구성하고 작업을 분배한다.

## Phase 0: 컨텍스트 확인

작업 시작 전 기존 산출물 여부를 확인한다:

- `_workspace/` 존재 + 부분 수정 요청 → **부분 재실행**: 해당 에이전트만 재호출
- `_workspace/` 존재 + 새 입력 제공 → **새 실행**: 기존 `_workspace/`를 `_workspace_prev/`로 이동 후 시작
- `_workspace/` 미존재 → **초기 실행**

## Phase 1: 작업 분석 및 계획

1. 사용자 요청에서 변경 영역을 식별한다:
   - 백엔드만 (API 수정, DB 스키마 등)
   - 프론트엔드만 (UI 수정, 뷰 추가 등)
   - 풀스택 (새 기능 = 백엔드 API + 프론트엔드 뷰)
2. Neo에게 사전 보고(수행 계획, 주의 사항)를 제시하고 확인을 받는다.
3. 단순 버그 수정이나 소규모 변경은 직접 처리하고, 팀 구성이 필요한 작업만 Phase 2로 진행한다.

## Phase 2: 팀 구성 및 작업 분배

**실행 모드: 에이전트 팀**

```
mfs-lead (리더)
  ├── backend-engineer  ← FastAPI API 구현
  ├── frontend-engineer ← Vue 뷰/컴포넌트 구현
  └── qa-reviewer       ← 통합 정합성 검증
```

작업 할당 원칙:
- backend-engineer와 frontend-engineer는 **병렬로 시작**한다. 단, frontend가 API spec에 의존하는 경우 backend-engineer가 `_workspace/api-spec.md`를 먼저 작성한다.
- qa-reviewer는 각 모듈 완성 직후 점진적으로 실행한다 (전체 완성 후 1회 X).

## Phase 3: 백엔드 구현

backend-engineer가 담당한다. `backend-dev` 스킬 참조.

산출물:
- 구현된 FastAPI 라우터/모델 코드
- `_workspace/api-spec.md` (프론트엔드가 사용할 API 명세)

## Phase 4: 프론트엔드 구현

frontend-engineer가 담당한다. `frontend-dev` 스킬 참조.

입력: `_workspace/api-spec.md` (backend-engineer 산출물)
산출물: 구현된 Vue 뷰/컴포넌트 코드

## Phase 5: QA 및 통합 검증

qa-reviewer가 담당한다.

- API 응답 shape ↔ 프론트 코드 교차 비교
- 보안 검토 (JWT, CORS, 입력값 검증)
- Vue 표준 준수 확인
- 산출물: `_workspace/qa-report.md`

## Phase 6: 최종 보고

mfs-lead가 종합하여 Neo에게 최종 보고:

```
[결과 리포트]
수행 내용: ...
변경 파일: ...
특이 사항: ...
```

## 데이터 전달

- 작업 디렉토리: `_workspace/` (중간 산출물 저장)
- 파일명 컨벤션: `{phase}_{agent}_{artifact}.{ext}` (예: `03_backend_api-spec.md`)
- 팀 내 통신: SendMessage (실시간) + 파일 기반 (구조화 산출물)

## 에러 핸들링

- 에이전트 1회 실패 시 재시도 1회
- 재실패 시 해당 결과 없이 진행하고 최종 보고서에 명시
- 백엔드/프론트 간 API spec 불일치 발견 시 qa-reviewer가 즉시 mfs-lead에게 보고

## 테스트 시나리오

**정상 흐름:** "카드 내역에 검색 필터 기능 추가해줘"
1. mfs-lead: 계획 수립 (백엔드 API 수정 + 프론트 뷰 수정)
2. backend-engineer: card_usage 라우터에 query param 추가
3. frontend-engineer: CardUsageView.vue에 필터 UI 추가
4. qa-reviewer: 응답 스키마 ↔ 프론트 필드 접근 검증
5. mfs-lead: 최종 보고

**에러 흐름:** backend-engineer 실패 시
1. 1회 재시도
2. 재실패 시 frontend-engineer에게 "백엔드 미완성, 모의 데이터로 UI만 구현" 지시
3. 최종 보고에 "백엔드 미완성 - 별도 수동 구현 필요" 명시
