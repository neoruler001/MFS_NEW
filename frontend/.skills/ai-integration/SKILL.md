---
name: AI 솔루션 연동 (AI Integration)
description: LLM 및 AI 기능을 프론트엔드에 통합하기 위한 설계 지침입니다.
---

# AI 솔루션 연동 Skill

## 1. 데이터 파이프라인
- **데이터 정제**: UI에서 생성된 데이터를 AI가 이해하기 쉬운 구조화된 JSON 형태로 변환하여 API에 전달합니다.
- **컨텍스트 추출**: 현재 페이지의 상태나 사용자의 이전 활동 기록을 컨텍스트로 포함시켜 답변의 정확도를 높입니다.

## 2. 스트리밍 처리 (Streaming Response)
- LLM의 긴 응답 대기 시간을 해소하기 위해 SSE(Server-Sent Events) 또는 Fetch HTTP Streaming API 처리를 권장합니다.
- 실시간으로 갱신되는 텍스트를 처리하기 위한 전용 Composable을 구현하여 사용합니다.

## 3. 프롬프트 관리
- 비즈니스 로직 내에 프롬프트 문자열을 직접 작성하지 않고, 전용 관리 파일(`src/utils/prompts.js`) 등을 통해 체계적으로 관리합니다.
