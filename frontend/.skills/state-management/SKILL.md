---
name: 상태 관리 (State Management)
description: Pinia를 활용한 전역 상태 관리 및 영속성 유지 전략입니다.
---

# 상태 관리 Skill

## 1. Pinia Store 정의
- `defineStore`를 사용하여 모듈화된 스토어를 구성합니다.
- 스토어 파일은 `src/store` 또는 `@core/utils` 등에 위치하며, `use[Name]Store` 명명 규칙을 따릅니다.

## 2. 데이터 영속성 (Persistence)
- 사용자 인증 정보나 환경 설정과 같이 새로고침 후에도 유지되어야 하는 데이터는 `pinia-plugin-persistedstate`를 사용하도록 설정합니다.

## 3. 반응성 유지
- 컴포넌트에서 스토어의 값을 가져올 때 구조 분해 할당을 하려면 `storeToRefs`를 사용하여 반응성이 깨지지 않도록 주의합니다.

```javascript
import { useUserStore } from '@/utils/user-store'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()
const { user, sessionId } = storeToRefs(userStore)
```
