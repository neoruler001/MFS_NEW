---
name: 프로젝트 아키텍처 (Project Architecture)
description: 프로젝트의 디렉토리 구조 및 핵심 라이브러리 활용 가이드라인입니다.
---

# 프로젝트 아키텍처 Skill

이 Skill은 `hax_web-client` 프로젝트의 일관된 구조를 유지하기 위한 지침을 제공합니다.

## 1. 주요 디렉토리 구조
- **`@core`**: 템플릿 레이아웃과 핵심 유틸리티가 위치합니다. 기본적으로 수정보다는 상속/확장하여 사용합니다.
- **`src/@layouts`**: 레이아웃 컴포넌트(Header, Sidebar, Footer 등) 전용 공간입니다.
- **`src/api`**: 모든 외부 API 호출 함수를 모듈별로 관리합니다.
- **`src/plugins`**: Vite, Vue, Iconify 등 각종 플러그인 설정이 위치합니다.
- **`src/utils`**: 비즈니스 로직과 무관한 순수 유틸리티 함수(Date 포맷팅 등)를 관리합니다.

## 2. 모듈 관리 원칙
- 모든 API 호출은 개별 파일별로 `Api` 접미사를 붙여 export 합니다.
- 컴포넌트는 `src/components`와 `src/views`로 나누어 재사용성과 페이지 단위를 구분합니다.
