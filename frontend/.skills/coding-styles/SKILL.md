---
name: 코딩 스타일 및 Git 규칙 (Coding/Git Styles)
description: 협업 생산성을 높이기 위한 코드 작성 관례 및 커밋 규칙입니다.
---

# 코딩 스타일 및 Git 규칙 Skill

## 1. 명명 규칙 (Naming)
- **변수 및 함수**: `camelCase` (예: `userEmail`, `getUserInfo`)
- **클래스 및 컴포넌트**: `PascalCase` (예: `UserLogin`, `CommonHistory`)
- **파일명**: 기본적으로 `kebab-case`를 사용하되, Vue 컴포넌트 파일은 `PascalCase`를 권장합니다.
- **상수**: `SCREAMING_SNAKE_CASE` (예: `MAX_RETRIES`)

## 2. 컴포넌트 작성 원칙
- **HOC (Hook-oriented Component)**: 함수형 스타일보다 Composition API (`<script setup>`) 기반의 훅 중심 개발을 권장합니다.
- **파일 구조 순서**: `.vue` 파일 내에서 다음 순서를 엄격히 준수합니다.
  1. `<script setup>` (참조 및 로직)
  2. `<template>`
  3. `<style>`

## 3. 코드 포맷팅 및 주석
- **포맷팅**: 2 spaces 들여쓰기, 세미콜론 사용, 홑따옴표(`'`) 사용.
- **주석**: '무엇'보다 '왜' 하는지를 설명하며, 기술적 부채는 `// TODO(이름, 날짜): 내용` 형식으로 관리합니다.

## 4. Git 커밋 컨벤션
- 일관된 히스토리 관리를 위해 Angular Commit Guidelines를 따릅니다.
  - `feat`: 기능 추가, `fix`: 버그 수정, `docs`: 문서, `style`: 포맷팅, `refactor`: 리팩토링, `test`: 테스트, `chore`: 빌드/설정.
