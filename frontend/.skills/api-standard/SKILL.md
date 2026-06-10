---
name: API 통신 표준 (API Interaction Standard)
description: Axios 및 VueUse 기반의 비동기 통신 및 에러 처리 가이드라인입니다. (통신 패턴 우선순위 및 인증/에러 처리 규칙 포함)
---

# API 통신 표준 Skill

## 1. Axios Utility (`@/utils/axios`)
- 우선순위(Precedence):
  1. 표준 API 호출은 항상 `@/utils/axios` 인스턴스를 사용합니다.
  2. 컴포넌트 내에서 반응형 데이터가 필요하고 대상 백엔드가 `Authorization: Bearer` 기반일 때만 `useApi`를 사용합니다.
  3. 동일한 요청 경로에서 두 패턴을 혼용하지 않습니다.

- **인스턴스 사용(명확화)**: 모든 HTTP 요청 함수(서비스 함수, composables, store action, helper 포함)는 반드시 `import axios from '@/utils/axios'`로 제공되는 커스텀 인스턴스를 사용해야 하며, raw `axios` 또는 `axios.create`를 직접 import하지 않습니다.
- **토큰 자동 주입(범위 명시)**: `@/utils/axios`의 Request 인터셉터는 표준(non-Bearer) 백엔드 호출에 대해 쿠키(`accessToken`)를 확인하여 `X-Auth-Token` 헤더를 추가합니다. Bearer 인증이 필요한 엔드포인트는 `useApi`(아래)를 사용하십시오.
- **토큰 부재/만료 처리**: 인터셉터에서 `accessToken`이 없거나 만료/무효로 판단되면 요청을 중단하고 401 에러를 반환합니다. 사용자에게는 '로그인 후 다시 시도해주세요' 메시지를 표시합니다.
- **데이터 반환**: Response 인터셉터에서 `response.data`를 반환하므로, 호출부는 추가 `.data` 접근이 필요 없습니다.

## 2. VueUse `useApi` (`@/composables/useApi`)
- 사용 조건: 컴포넌트 내에서 반응형 상태(loading, data, error)가 필요하고, 대상 백엔드가 `Authorization: Bearer` 인증을 요구하며 `baseURL`이 `https://api.example.com`와 같이 명시된 경우에만 사용합니다.
- 역할 분리: `useApi`는 Bearer 토큰(`Authorization: Bearer <token>`)을 사용해 요청을 수행하며, 동일한 요청 경로에서 `@/utils/axios` 인스턴스와 혼용해서는 안 됩니다.

## 3. 에러 처리 및 전역 관리 (Global Error Handling)
- **Centralized UI**: 에러 발생 시 컴포넌트별 로컬 메시지 대신 전역 에러 모달/토스트로 일관된 메시지를 노출합니다.
- **상태별 메시지 매핑(명확화)**:
  - 400: '잘못된 요청입니다. 입력을 확인해주세요.'
  - 401/403: '로그인 후 다시 시도해주세요.'
  - 500/502/503: '잠시 후 다시 시도해주세요.'
  - Network Error: '인터넷 연결을 확인해주세요.'
- **재시도 정책**:
  - 네트워크 실패의 경우 사용자에게 '다시 시도' 버튼을 제공하며, 최대 2회 수동 재시도를 허용합니다.
  - 401/403에 대해서는 자동 재시도 금지; 로그인/권한 확인 안내를 우선합니다.
  - 서버 5xx는 사용자에게 재시도를 권장하되 자동 재시치는 적용하지 않습니다.
- **전역 반환**: 매핑된 사용자 메시지는 글로벌 에러 핸들러를 통해 호출자에게 반환됩니다.

## 4. 특수 연동 패턴: 이메일 전송 웹훅 (Email Sharing)
- 콘텐츠를 이메일로 전송할 때 사용하는 표준 페이로드 구조 및 검증 규칙입니다.
- **Payload 스키마(명시)**: 이메일 웹훅은 다음 JSON 형식을 사용합니다:

```json
{
  "to": ["user@example.com"],
  "subject": "제목",
  "body": "본문 내용",
  "metadata": { "source": "ui", "templateId": "optional-template-id" }
}
```

- 필수 항목: `to`(string[]), `subject`(string), `body`(string), `metadata.source`(string).
- **Validation(클라이언트)**: 클라이언트는 이메일 정규표현식으로 각 수신자 형식을 검증하고, 중복 수신자를 제거 또는 거부합니다. 잘못된 이메일 형식 또는 중복 수신자가 발견되면 클라이언트에서 전송을 차단하고 명확한 검증 오류를 반환합니다.

```javascript
import axios from '@/utils/axios'

export const fetchDataApi = async (id) => {
  try {
    return await axios.get(`/data/${id}`)
  } catch (error) {
    throw error
  }
}
```
