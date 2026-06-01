---
name: 반응형 스타일 표준 (Responsive Styling Standard)
description: 모든 뷰포트에서 일관된 레이아웃과 타이포그래피를 제공하기 위한 가이드라인입니다.
---

# 반응형 스타일 표준 Skill

## 1. 뷰포트 기준 (Breakpoints)
- **Mobile (xs)**: `0px` ~ `599px`
- **Tablet (sm, md)**: `600px` ~ `1279px`
- **Web (lg+)**: `1280px` 이상

## 2. 유동적 타이포그래피 (Fluid Typography)
- 뷰포트 크기에 따라 폰트 사이즈가 유동적으로 변하도록 `clamp()` 함수 사용을 권장합니다.
- 예: `font-size: clamp(1.5rem, 4vw + 1rem, 3rem);`

## 3. 간격 및 레이아웃 (Spacing & Layout)
- **Grid**: Vuetify의 `VRow`, `VCol`을 사용하여 반응형 컬럼을 구성합니다.
- **Spacing**: 모바일에서는 `pa-4`, 웹에서는 `pa-8` 등 뷰포트별 적절한 여백을 적용합니다.

## 4. 적용 예시
```css
@media (max-width: 599px) {
  .responsive-container {
    padding: 16px;
  }
}
@media (min-width: 1280px) {
  .responsive-container {
    padding: 32px;
  }
}
```
