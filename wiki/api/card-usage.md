# 카드 이용내역 API — /api/v1/cards

**파일**: `backend/app/api/card_usage.py`  
**SAP 인터페이스**: XFI00250, XFI00260, XFI00270, XFI00280

모든 엔드포인트는 JWT 인증이 필요합니다 (`Authorization: Bearer {token}`).

---

## GET /api/v1/cards/usages

카드 이용내역을 조회합니다. (SAP XFI00250 호출)

### 요청 파라미터 (Query)

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| card_num | string | `""` | 카드 번호 (미입력 시 전체) |
| fr_date | string | `""` | 조회 시작일 (YYYYMMDD) |
| to_date | string | `""` | 조회 종료일 (YYYYMMDD) |
| pi_status | string | `"A"` | 상태 (`A`=전체) |

### 응답 (200 OK)

```json
[
  {
    "BUKRS": "1000",
    "CARD_NUMC": "1234567890123456",
    "APPR_DATE": "20260601",
    "APPR_NUMC": "12345678",
    "AMOUNT": "50000",
    "MERCHANT": "스타벅스",
    "STATUS": "A",
    "SGTXT": ""
  }
]
```

### 처리 흐름

```
read_card_usages()
  → get_current_user()       [JWT에서 target_pernr 추출]
  → call_xfi00250({
      PI_PERNR_O: current_user.username,
      PI_PERNR_R: current_user.target_pernr,
      PI_FR_DATE: fr_date,
      PI_TO_DATE: to_date,
      PI_STATUS: pi_status
    })
  ← TE_CARD_USE 배열 반환
```

---

## GET /api/v1/cards/card-info

카드 기본 정보를 조회합니다. (SAP XFI00250 호출, PI_CARD_NUMC="X" 모드)

### 응답 (200 OK)

```json
[
  {
    "CARD_NUMC": "1234567890123456",
    "CARD_TYPE": "개인법인카드",
    "BUKRS": "1000"
  }
]
```

---

## GET /api/v1/cards/worklist

비용처리 팝업에서 사용하는 업무목록을 조회합니다. (SAP XFI00280 호출)

### 요청 파라미터 (Query)

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| bukrs | string | 필수 | 회사 코드 |

### 응답 (200 OK)

```json
{
  "TE_TEMPLATE": [...],
  "TE_SGTXT": [...],
  "TE_DOCPR_SGTXT": [...]
}
```

---

## POST /api/v1/cards/process

선택한 카드 이용내역을 SAP에 비용처리(전표 생성)합니다. (SAP XFI00260 호출)

### 요청 Body

```json
{
  "items": [
    {
      "BUKRS": "1000",
      "APPR_DATE": "20260601",
      "CARD_NUMC": "1234567890123456",
      "APPR_NUMC": "12345678",
      "CANC_FLAG": "",
      "SEQN_NUMC": "1",
      "DOCPR": "ABCD",
      "PERNR": "BP12345",
      "SGTXT": "업무용 커피"
    }
  ]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| BUKRS | string | 필수 | 회사 코드 |
| APPR_DATE | string | 필수 | 승인 일자 (YYYYMMDD) |
| CARD_NUMC | string | 필수 | 카드 번호 |
| APPR_NUMC | string | 필수 | 승인 번호 |
| CANC_FLAG | string | 선택 | 취소 플래그 (기본값 `""`) |
| SEQN_NUMC | string | 선택 | 순번 |
| DOCPR | string | 필수 | 업무 코드 (worklist에서 선택) |
| PERNR | string | 필수 | 사번 |
| SGTXT | string | 선택 | 적요 텍스트 |

> 한 번에 최대 100건까지 처리 가능합니다.

### 응답 (200 OK)

```json
{
  "PE_RESULT": "S",
  "PE_MESSAGE": "처리가 완료되었습니다.",
  "T_DATA": [
    {
      "APPR_NUMC": "12345678",
      "MSG_TYPE": "S",
      "MSG_TXT": "전표 생성 완료"
    }
  ]
}
```

| 필드 | 설명 |
|------|------|
| PE_RESULT | `S` = 성공, `E` = 오류 |
| PE_MESSAGE | 처리 결과 메시지 |
| T_DATA | 항목별 처리 결과 배열 |

---

## POST /api/v1/cards/cancel

비용처리된 내역을 취소합니다. (SAP XFI00270 호출)

### 요청 Body

```json
{
  "items": [
    {
      "BUKRS": "1000",
      "BELNR": "9000000001",
      "GJAHR": "2026",
      "CARD_NUMC": "1234567890123456",
      "APPR_DATE": "20260601",
      "APPR_NUMC": "12345678",
      "CANC_FLAG": "X",
      "SEQN_NUMC": "1",
      "PERNR": "BP12345"
    }
  ]
}
```

### 응답 (200 OK)

process와 동일 구조 (`PE_RESULT`, `PE_MESSAGE`, `T_DATA`)

---

## Vue 호출 예시 (CardUsageView.vue)

```javascript
// 카드 이용내역 조회
const fetchUsages = async () => {
  const res = await axios.get('/api/v1/cards/usages', {
    params: { fr_date: '20260601', to_date: '20260630', pi_status: 'A' }
  })
  usages.value = res.data
}

// 비용처리
const processExpenses = async () => {
  const res = await axios.post('/api/v1/cards/process', {
    items: selectedItems.value
  })
  if (res.data.PE_RESULT === 'S') {
    alert('비용처리가 완료되었습니다.')
  } else {
    alert('처리 실패: ' + res.data.PE_MESSAGE)
  }
}
```
