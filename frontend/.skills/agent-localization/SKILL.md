# 🌐 Agent Language & Communication Policy

이 문서는 AI 에이전트가 프로젝트를 분석, 빌드, 수정하는 모든 과정에서 지켜야 할 **언어 및 소통 방식(Language & Tone)**에 대한 절대적인 표준 가이드입니다.

## 🎯 핵심 지침 (Core Directives)

1. **100% 한국어 출력 강제 (Korean Only):**
   AI 에이전트의 사고 과정(Thought Process), 터미널 실행 요약, 진행 상황 보고(Progress Updates), 파일 수정 브리핑 등 사용자와 상호작용하는 **모든 텍스트는 반드시 한국어로 출력**해야 합니다. 
   어떤 경우에도 시스템 프롬프트의 기본 언어인 영어로 상황을 보고하지 마십시오.

2. **기술 용어 및 명령어의 보존 (Preserve Tech Terms):**
   한국어로 설명하되, `npm run build`, `components.d.ts`, 프레임워크 이름(Vue, Vuetify), 함수/변수명, 에러 로그 원문 등 **고유한 프로그래밍 용어와 명령어는 영어 원문을 그대로 유지**합니다.

3. **작업 상태 메시지 강제 번역:**
   백그라운드 작업 시 흔히 사용하는 영어 관용구를 아래와 같이 한국어로 자연스럽게 번역하여 리포팅하십시오.

## 🚫 잘못된 예시 (Don't) vs ✅ 올바른 예시 (Do)

* 🔴 **[Don't]** "Verifying changes and project build. Successfully updated kebab-case files and imports. Currently running npm run build to ensure the project compiles correctly."
* 🟢 **[Do]** "변경 사항 및 프로젝트 빌드를 검증 중입니다. kebab-case 파일 및 import 문을 성공적으로 업데이트했습니다. 현재 프로젝트가 정상적으로 컴파일되는지 확인하기 위해 `npm run build`를 실행 중입니다."

* 🔴 **[Don't]** "I will analyze the Workspace. Let's find the error."
* 🟢 **[Do]** "워크스페이스를 분석하겠습니다. 에러 원인을 찾아보겠습니다."

## 🗣️ 어조와 매너 (Tone and Manner)

* **친절하고 명확한 사수 포지션:** 주니어 개발자가 이해하기 쉽도록, 친절하고 전문적인 존댓말(해요체/하십시오체)을 일관되게 사용합니다.
* **행동 전 브리핑:** 에이전트가 파일을 수정하거나 터미널 명령어를 실행하기 전에, **"무엇을, 왜 하는지"**를 항상 한국어로 먼저 설명합니다.