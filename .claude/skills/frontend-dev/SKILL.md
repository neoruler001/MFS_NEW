---
name: MFS 프론트엔드 개발 표준
description: >
  MFS Vue 3 프론트엔드 개발 시 적용하는 표준이다.
  새 뷰 추가, 컴포넌트 수정, 라우터 변경, API 연동, UI 구현 작업에 반드시 이 스킬을 참조한다.
  frontend-engineer 에이전트가 주로 사용하며, 프론트엔드 직접 작업 시에도 적용한다.
---

# MFS 프론트엔드 개발 표준

## 프로젝트 구조

```
frontend/
├── src/
│   ├── App.vue           # 루트 컴포넌트
│   ├── main.js           # 앱 진입점
│   ├── router/
│   │   └── index.js      # Vue Router (createRouter, beforeEach 가드)
│   └── views/            # 페이지 단위 뷰
│       ├── LoginView.vue
│       ├── HomeView.vue
│       ├── CardUsageView.vue
│       ├── BudgetView.vue
│       ├── NoticeView.vue
│       ├── ContactView.vue
│       └── AdminView.vue
├── public/
├── index.html
└── vite.config.js
```

## Vue SFC 작성 패턴

**파일 구조 순서 (엄수):** `<script setup>` → `<template>` → `<style scoped>`

```vue
<script setup>
import { ref, onMounted } from 'vue'

const items = ref([])
const loading = ref(false)

onMounted(async () => {
  await loadItems()
})

async function loadItems() {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/items', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('API 오류')
    items.value = await res.json()
  } catch (e) {
    alert('데이터를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <!-- 템플릿 -->
  </div>
</template>

<style scoped>
/* 도메인 특화 스타일만 */
</style>
```

## 명명 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수·함수 | camelCase | `cardItems`, `loadData` |
| 컴포넌트 파일 | PascalCase | `CardUsageView.vue` |
| 상수 | SCREAMING_SNAKE_CASE | `MAX_PAGE_SIZE` |
| CSS 클래스 | kebab-case | `card-table` |

## 인증 처리

- 토큰 저장: `localStorage.setItem('token', token)`
- 토큰 읽기: `localStorage.getItem('token')`
- API 요청 헤더: `Authorization: Bearer ${token}`
- 401 응답 처리: localStorage에서 token 제거 후 `/login`으로 redirect

```javascript
if (res.status === 401) {
  localStorage.removeItem('token')
  router.push({ name: 'login' })
  return
}
```

## 라우터 등록

새 뷰 추가 시 `src/router/index.js`에 다음 패턴으로 등록:

```javascript
{
  path: '/{경로}',
  name: '{이름}',
  component: () => import('../views/{뷰파일}.vue'),
  meta: { requiresAuth: true }  // 인증 필요 시
}
```

인증 불필요 페이지(로그인, 에러 등)는 `meta: { requiresAuth: true }` 생략.

## API 통신 패턴

- Base URL: `http://localhost:4101/api/v1` (개발) — vite.config.js proxy 설정 확인
- 인증 헤더: 모든 인증 필요 요청에 `Authorization: Bearer {token}` 첨부
- 에러 처리: HTTP 상태 코드로 분기 (401 → 로그인 리다이렉트, 기타 → 사용자 메시지 표시)

## 에러 처리 패턴

```javascript
try {
  const res = await fetch(url, options)
  if (res.status === 401) {
    localStorage.removeItem('token')
    router.push({ name: 'login' })
    return
  }
  if (!res.ok) {
    throw new Error(`서버 오류: ${res.status}`)
  }
  const data = await res.json()
  // 성공 처리
} catch (e) {
  console.error(e)
  alert('요청 처리 중 오류가 발생했습니다.')
}
```

## 기존 스킬 참조

`frontend/.skills/` 하위의 기존 스킬도 유효하다. 작업 전 관련 스킬을 읽는다:
- `coding-styles/`: 코딩 스타일 상세 규칙
- `component-architecture/`: 컴포넌트 구조 상세
- `design-system/`: 디자인 시스템
- `responsive-styling/`: 반응형 스타일링
- `testing-validation/`: 테스트 및 검증
