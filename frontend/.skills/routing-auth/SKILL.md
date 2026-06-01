---
name: 라우팅 및 인증 (Routing & Auth)
description: 자동 라우팅 시스템과 내비게이션 가드를 통한 보안 관리 지침입니다.
---

# 라우팅 및 인증 Skill

## 1. 자동 라우팅 시스템
- `unplugin-vue-router`를 탑재하여 `src/pages` 하위의 파일 구조가 자동으로 라우트 경로가 됩니다.
- 레이아웃은 `virtual:generated-layouts`를 통해 각 페이지 컴포넌트의 메타 정보에 따라 결정됩니다.

## 2. 내비게이션 가드 (Navigation Guards)
- **인증 체크**: `beforeEach`에서 `userStore.sessionId`를 확인하여 로그인이 필요한 페이지 접근을 제어합니다.
- **권한 제어**: 사용자의 메뉴 권한(`auth`)과 라우트 이름(`to.name`)을 대조하여 권한이 없는 경우 에러 페이지로 유도합니다.
- **접근 로그**: 모든 성공적인 페이지 전환에 대해 `storeAccessLogApi`를 호출하여 서버에 로그를 남깁니다.

## 3. 인증 예외 처리
- 로그인 페이지, 에러 페이지, 약관 등 인증 없이 접근 가능한 경로는 가드 로직에서 예외 처리합니다.
