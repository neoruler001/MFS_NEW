# 카드 이용내역 API

**Base path:** `/api/v1/cards`  
**파일:** `backend/app/api/card_usage.py`  
**데이터 소스:** SAP ERP (SOAP)

> 모든 엔드포인트는 JWT 인증 필요

---

## GET /usages

카드 이용내역 목록 조회.

**SAP 인터페이스:** `XFI00250`

### 요청 파라미터

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `fr_date` | string | 조회 시작일 (YYYYMMDD) |
| `to_date` | string | 조회 종료일 (YYYYMMDD) |
| `pi_status` | string | 처리 상태 필터 |

### 응답

```json
[
  {
    "CARD_NUMC": "9411-****-****-1234",
    "APPR_DATE": "20260610",
    "APPR_NUMC": "12345678",
    "AMOUNT": "50000",
    "MERCHANT": "스타벅스",
    "STATUS": "미처리"
  }
]
```

---

## GET /info

카드 기본 정보 조회.

**SAP 인터페이스:** `XFI00250` (카드정보 파라미터)

---

## GET /worklist

비용처리 업무목록(회사코드별) 조회.

**SAP 인터페이스:** `XFI00280`

### 요청 파라미터

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `bukrs` | string | 회사코드 (SAP BUKRS) |

---

## POST /process

카드 이용건 비용처리 (SAP 전표 생성).

**SAP 인터페이스:** `XFI00260`

### 요청

```json
{
  "items": [
    {
      "BUKRS": "1000",
      "APPR_DATE": "20260610",
      "CARD_NUMC": "9411****1234",
      "APPR_NUMC": "12345678",
      "DOCPR": "...",
      "PERNR": "BP26745",
      "SGTXT": "업무용 미팅비"
    }
  ]
}
```

### 응답

```json
{
  "PE_RESULT": "S",
  "PE_MESSAGE": "처리 완료",
  "T_DATA": [...]
}
```

> `PE_RESULT = "S"` 이면 성공, `"E"` 이면 오류. SAP 오류 메시지는 `PE_MESSAGE`에 포함.

---

## POST /cancel

비용처리 취소 (SAP 전표 취소).

**SAP 인터페이스:** `XFI00270`

### 요청

```json
{
  "items": [
    {
      "BUKRS": "1000",
      "APPR_DATE": "20260610",
      "CARD_NUMC": "9411****1234",
      "APPR_NUMC": "12345678"
    }
  ]
}
```

---

## 처리 흐름 요약

```
Vue CardUsageView
  ↓ (1) GET /worklist   → XFI00280 → 업무목록 선택
  ↓ (2) GET /usages     → XFI00250 → 이용내역 표시
  ↓ (3) POST /process   → XFI00260 → 선택 건 전표 생성
  ↓ (4) POST /cancel    → XFI00270 → 처리건 취소
```

모든 SAP 호출은 `soap_client._call_sap_soap(interface_id, xml_body)` 를 통해 단일 HTTP 클라이언트로 처리된다.
