# 예산 API

**Base path:** `/api/v1/budget`  
**파일:** `backend/app/api/budget.py`  
**데이터 소스:** SAP ERP (SOAP XFI00290)

> JWT 인증 필요

---

## GET /info

사원별 예산 정보 조회.

**SAP 인터페이스:** `XFI00290`

### 내부 처리

```python
current_user = Depends(get_current_user)
# JWT의 target_pernr를 SAP 파라미터로 전달
# → 대리 조회 시 위임된 대상 사번이 사용됨
result = soap_client.call_xfi00290(pernr=current_user.target_pernr)
```

### 응답

SAP XFI00290 반환값 그대로 전달 (구조는 SAP 인터페이스 정의 참조).

---

## 참고

예산 데이터는 전적으로 SAP ERP에서 관리된다. MSSQL에는 예산 관련 테이블이 없다.

대리 조회 시나리오: 관리자가 `/auth/delegate`로 위임 토큰을 발급받으면, 이후 예산 조회도 대상 사번 기준으로 실행된다.
