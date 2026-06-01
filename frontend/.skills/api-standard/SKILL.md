---
name: API 통신 표준 (API Interaction Standard)
description: Axios 및 VueUse 기반의 비동기 통신 및 에러 처리 가이드라인입니다.
---

# API 통신 표준 Skill

## 1. Axios Utility (`@/utils/axios`)
- **인스턴스 사용**: 모든 API 함수는 `import axios from '@/utils/axios'`를 통해 정의된 커스텀 인스턴스를 사용해야 합니다.
- **토큰 자동 주입**: Request 인터셉터에서 쿠키(`accessToken`)를 확인하여 `X-Auth-Token` 헤더를 자동으로 추가합니다.
- **데이터 반환**: Response 인터셉터에서 `response.data`를 바로 반환하므로, API 호출 시 중첩된 `.data` 접근이 필요 없습니다.

## 2. VueUse `useApi` (`@/composables/useApi`)
- 컴포넌트 내에서 반응형 데이터와 함께 비동기 통신을 처리할 때 사용합니다.
- `Authorization: Bearer` 헤더를 사용하는 특정 백엔드 서비스와의 통신 시에 주로 활용됩니다.

## 3. 에러 처리 및 전역 관리 (Global Error Handling)
- **Centralized UI**: 에러 발생 시 개별 컴포넌트가 아닌, 전역 에러 모달/토스트를 통해 일관된 메시지를 노출합니다.
- **사용자 친화적 메시지**: 상세한 기술적 에러(500, Network Error) 대신 사용자가 이해할 수 있는 행동 가이드를 제공합니다.
- **재시도 로직**: 네트워크 오류 시 '다시 시도' 버튼을 제공하여 UX를 개선합니다.

## 4. 특수 연동 패턴: 이메일 전송 웹훅 (Email Sharing)
- 콘텐츠를 이메일로 전송할 때 사용하는 표준 페이로드 구조입니다.
- **Payload**: 수신자 목록, 제목, 본문, 메타데이터를 포함한 JSON 규격을 따릅니다.
- **Validation**: 클라이언트에서 이메일 형식(Regex)과 다중 수신자 중복 여부를 1차 검증합니다.

```javascript
export const fetchDataApi = async (id) => {
  try {
    return await axios.get(`/data/${id}`)
  } catch (error) {
    throw error
  }
}
```
