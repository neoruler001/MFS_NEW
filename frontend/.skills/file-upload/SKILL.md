---
name: 파일 업로드 및 유효성 검사 (File Upload & Validation)
description: 안전하고 사용자 친화적인 파일 업로드 환경을 구축하기 위한 가이드라인입니다.
---

# 파일 업로드 및 유효성 검사 Skill

## 1. 클라이언트 단 유효성 검사
- **용량 제한**: `file.size`를 체크하여 서버 부하를 방지합니다.
- **확장자 제한**: `file.name`에서 확장자를 추출하여 허용된 형식인지 확인합니다.
- **즉시 피드백**: 파일 선택 직후 유효성 결과를 사용자에게 안내합니다.

## 2. 구현 패턴
```javascript
const validateFile = (file) => {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const allowedTypes = ['image/png', 'image/jpeg', 'application/pdf'];

  if (file.size > maxSize) return '파일 용량이 너무 큽니다.';
  if (!allowedTypes.includes(file.type)) return '지원하지 않는 파일 형식입니다.';
  
  return null;
};
```

## 3. 다중 파일 업로드 관리
- **Queue**: 업로드 대기 목록을 UI로 노출합니다.
- **Progress**: 개별 파일 또는 전체 진행 상황을 퍼센트(%)로 표시합니다.
- **Status**: 성공/실패 여부를 명확히 구분하여 표시합니다.
