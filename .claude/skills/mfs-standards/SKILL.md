---
name: MFS 프로젝트 표준 (코딩·보안·Git)
description: >
  MFS 프로젝트 전반의 코딩 스타일, 보안 원칙, Git 커밋 컨벤션 표준이다.
  코드 리뷰, 표준 위반 지적, 커밋 메시지 작성, 보안 검토 요청 시 이 스킬을 참조한다.
  "표준에 맞게", "컨벤션", "코드 리뷰", "커밋 메시지", "보안 확인" 등의 표현에 적용한다.
---

# MFS 프로젝트 표준

## 코딩 스타일

### 공통
- 들여쓰기: 2 spaces (Python은 4 spaces)
- 세미콜론: JavaScript는 사용, Python은 불필요
- 문자열: JavaScript는 홑따옴표(`'`), Python은 더블쿼트(`"`)
- 주석: '무엇'이 아닌 '왜'를 설명한다. 기술 부채는 `// TODO(이름, 날짜): 내용` 형식.

### Python (백엔드)
- 명명: 변수·함수 `snake_case`, 클래스 `PascalCase`, 상수 `SCREAMING_SNAKE_CASE`
- 타입 힌트: 함수 파라미터와 반환값에 타입 힌트를 명시한다
- 환경: `uv` 기반 가상환경 (`backend/.venv/`)

### JavaScript/Vue (프론트엔드)
- 명명: 변수·함수 `camelCase`, 컴포넌트 파일 `PascalCase`, CSS 클래스 `kebab-case`
- Vue: Composition API (`<script setup>`) 전용, Options API 금지
- 파일 순서: `<script setup>` → `<template>` → `<style scoped>`

## 보안 원칙 (OWASP Top 10 기반)

### A01 접근 제어
- 모든 인증 필요 API에 `Depends(get_current_user)` 적용
- 관리자 전용 기능은 `is_admin` 필드로 권한 분리

### A03 인젝션
- SQL: ORM 메서드만 사용, raw SQL 쿼리 금지
- XSS: 사용자 입력을 HTML에 직접 삽입 금지 (Vue의 `v-html` 최소화)

### A05 보안 설정 오류
- CORS: `allow_origins=["*"]`는 개발 전용. 운영 배포 전 특정 도메인으로 제한
- 에러 메시지: 500 응답에 스택 트레이스, DB 쿼리, 내부 경로 노출 금지

### A07 인증 및 세션 관리
- JWT: SECRET_KEY는 `.env`에 저장, 코드에 하드코딩 금지
- 토큰 만료: 30분 (운영 환경에서 조정 가능)
- 비밀번호: bcrypt 해싱 필수 (`app/core/security.py`)

### A09 로깅 및 모니터링
- 인증 실패, 권한 없는 접근 시도를 로그에 기록한다
- 민감 정보(비밀번호, 토큰 원문)를 로그에 남기지 않는다

## Git 커밋 컨벤션 (Angular 스타일)

### 형식
```
{type}: {subject}

{body (선택)}
```

### 타입 목록
| 타입 | 설명 |
|------|------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `style` | 포맷팅, 세미콜론 등 (기능 변경 없음) |
| `refactor` | 리팩토링 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드 설정, 패키지 관리 등 |
| `security` | 보안 취약점 수정 |

### 예시
```
feat: 카드 내역 검색 필터 API 추가
fix: 로그인 후 뒤로가기 시 토큰 만료 오류 수정
security: CORS 허용 도메인 운영 환경 특정 도메인으로 제한
```

## 표준 위반 시 대응

표준 위반 발견 시:
1. 위반 내용과 해당 표준 문서를 명시한다
2. 수정 방법을 제시한다
3. Critical 보안 위반(하드코딩된 시크릿, raw SQL)은 즉시 수정을 요청한다

## 에이전트 출력 언어 정책

- 모든 에이전트의 사고 과정, 진행 상황 업데이트, 작업 완료 요약은 **한국어**로 작성한다
- 코드, 명령어, 파일명은 영어 원문 유지
- 사용자 호칭: "Neo"
