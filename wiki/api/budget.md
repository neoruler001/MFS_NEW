# 예산 API — /api/v1/budget

**파일**: `backend/app/api/budget.py`  
**SAP 인터페이스**: XFI00290

---

## GET /api/v1/budget/budget

예산 현황을 조회합니다.

**인증 필요**: 예

### 요청 파라미터 (Query)

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| bukrs | string | `""` | 회사 코드 |
| objnr | string | `""` | 오브젝트 번호 |
| objty | string | `""` | 오브젝트 타입 |
| kstar | string | `""` | 비용 원소 |
| gjahr | string | `""` | 회계연도 (YYYY) |
| i_system | string | `""` | 시스템 구분 |

### 응답 (200 OK)

```json
{
  "...": "..."
}
```

> ⚠️ XFI00290의 응답 구조는 동적입니다. 런타임에 키를 탐색하며, 실제 SAP 응답에 따라 구조가 다를 수 있습니다.

### 처리 흐름

```
read_budget()
  → get_current_user()     [JWT에서 target_pernr 추출]
  → call_xfi00290({
      PI_BUKRS: bukrs,
      PI_PERNR: current_user.target_pernr,
      PI_OBJNR: objnr,
      PI_OBJTY: objty,
      PI_KSTAR: kstar,
      PI_GJAHR: gjahr,
      I_SYSTEM: i_system,
      PI_CALLSYS: 'P'
    })
  ← SAP 응답 그대로 반환
```
