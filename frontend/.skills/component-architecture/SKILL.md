---
name: 컴포넌트 아키텍처 (Component Architecture)
description: Vue 3 Composition API 및 Vuetify 기반의 UI 개발 가이드라인입니다.
---

# 컴포넌트 아키텍처 Skill

## 1. 기본 원칙
- **SFC & Script Setup**: 모든 컴포넌트는 단일 파일 컴포넌트(.vue) 형식이며 `<script setup>`을 사용합니다.
- **PascalCase**: 컴포넌트 파일명과 템플릿 태그 내 호출은 `PascalCase`를 따릅니다.

## 2. UI 개발 (Vuetify 3)
- 가능한 한 Vuetify 3에서 제공하는 표준 컴포넌트(`VCard`, `VBtn`, `VDataTable` 등)를 사용합니다.
- 도메인 특화 스타일이 필요한 경우에만 최소한의 커스텀 CSS를 작성합니다.

## 3. Props & Emits 정의
- `defineProps`, `defineEmits`를 사용하여 데이터와 이벤트를 명확히 명시합니다.

## 4. 아이콘 활용 (Iconify)
- `VIcon` 컴포넌트와 `icon` 속성을 통해 Iconify 아이콘 시스템을 일관되게 적용합니다.

```vue
<template>
  <VBtn color="primary" @click="handleClick">
    <VIcon icon="ri-check-line" start />
    Confirm
  </VBtn>
</template>
```
