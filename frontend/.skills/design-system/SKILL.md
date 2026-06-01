---
name: 디자인 시스템 (Design System)
description: 브랜드 일관성을 유지하고 최신 UI/UX 트렌드를 반영하기 위한 스타일링 가이드입니다.
---

# 디자인 시스템 Skill

## 1. 테마 및 디자인 토큰 (Design Tokens)

- **통합 관리**: 다크/라이트 모드, Primary 컬러 등 전역 테마 설정은 `themeConfig.js`에서 통합 관리합니다.
- **디자인 토큰 활용**: 하드코딩된 색상이나 간격 대신, 일관성 있는 시각 언어를 위해 정의된 디자인 토큰(CSS Variables)을 적극 활용하여 유지보수성을 높입니다.

## 2. 스타일 우선순위

1. **Vuetify 유틸리티 클래스**: Spacing(`pa-4`, `mt-2`), Typography(`text-h5`), Alignment 등을 최우선으로 사용하여 코드량을 줄이고 일관성을 유지합니다.
2. **공통 디자인 토큰 (Sass/CSS 변수)**: 커스텀 스타일링 시 공통으로 정의된 변수를 참조합니다.
3. **Custom CSS**: 불가피한 경우에만 `<style scoped>` 또는 CSS Module을 사용합니다.

## 3. 핵심 디자인 패턴 (Modern Trends)

### Bento Grid (벤토 그리드)

최신 대시보드 및 랜딩 페이지에서 각광받는 모듈형 카드 레이아웃입니다.

- **구조화**: 콘텐츠를 다양한 크기의 둥근 직사각형 셀(Cell)로 나누어 직관적으로 배치합니다.
- **반응형**: Grid 및 Flexbox를 활용해 화면 크기에 맞춰 셀 배치를 유동적으로 변경합니다.

### Advanced Glassmorphism & Spatial Design (공간감 디자인)

단순한 투명도를 넘어, 깊이감 있는 레이아웃을 구현합니다.

- **Backdrop Blur & Noise**: `backdrop-filter: blur(12px);`와 미세한 노이즈 텍스처를 결합해 리얼한 유리 질감 표현.
- **Layered Shadows**: 다중 `box-shadow`를 사용하여 요소 간의 Z-축 깊이감을 정밀하게 조정.
- **Subtle Borders**: 반투명한 그라데이션 테두리(`border: 1px solid rgba(255,255,255,0.15)`)로 엣지를 살립니다.

### Fluid/Mesh Gradients (오로라 그라데이션)

정적인 단일 그라데이션 대신, 유기적으로 혼합되는 다채로운 배경을 사용합니다.

- **자연스러운 혼합**: 3~4개의 테마 색상이 부드럽게 블렌딩되는 애니메이션을 배경이나 강조 요소(버튼, 카드 배경 등)에 적용합니다.

### Micro-interactions (마이크로 인터랙션)
6001
사용자 액션에 즉각적이고 디테일한 시각적 피드백을 제공합니다.

- **Hover/Active Effects**: 버튼 클릭 시 스케일 축소(`transform: scale(0.97)`), 호버 시 부드러운 Glow 효과.
- **Floating & Staggered**: `translateY`를 이용한 부드러운 상하 이동 및 리스트 요소 노출 시 `animation-delay`를 순차적으로 부여하여 리듬감 있는 등장.

## 4. 접근성 및 반응형 테마 (a11y & Dark Mode)

- **Dark/Light Mode**: CSS 변수(`[data-theme='dark']`)를 사용하여 테마 전환 시 색상과 투명도가 유기적으로 전환되도록 설계합니다.
- **Prefers-Reduced-Motion**: 사용자의 시스템 애니메이션 축소 설정을 존중하여, 해당 옵션 활성화 시 동적 애니메이션을 최소화합니다 (`@media (prefers-reduced-motion: reduce)`).
- **고대비 (High Contrast)**: 텍스트와 배경 간의 WCAG 명도 대비 기준을 충족하도록 색상 토큰을 설계합니다.
