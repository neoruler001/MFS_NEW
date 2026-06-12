# SAP SOAP 인터페이스

**SAP PI 엔드포인트:** `http://hipop.hhi.co.kr:50000/XISOAPAdapter/MessageServlet`  
**Sender Service:** `P_XIMOB`  
**Namespace:** `http://hhi.co.kr/FI/XIMOB`  
**인증:** HTTP Basic Auth (`INFPIUSR`)  
**타임아웃:** 30초

모든 SAP 호출은 `backend/app/core/soap_client.py`의 `_call_sap_soap()` 단일 진입점을 통해 처리된다.

---

## 인터페이스 목록

| ID | 설명 | 호출 함수 | 호출 위치 |
|----|------|----------|---------|
| **XFI00250** | 카드 이용내역 / 카드정보 조회 | `call_xfi00250` | `api/card_usage.py` |
| **XFI00260** | 비용처리 (전표 생성) | `call_xfi00260` | `api/card_usage.py` |
| **XFI00270** | 처리취소 (전표 취소) | `call_xfi00270` | `api/card_usage.py` |
| **XFI00280** | 업무목록 조회 | `call_xfi00280` | `api/card_usage.py` |
| **XFI00290** | 예산 조회 | `call_xfi00290` | `api/budget.py` |
| **XFI00310** | 연락처 조회 | `call_xfi00310` | `api/contact.py` |
| **XFI00320** | SAP 공지사항 조회 | `call_xfi00320` | `api/notice.py` |

---

## XFI00250 — 카드 이용내역/카드정보 조회

### 입력 파라미터

| 파라미터 | 설명 |
|----------|------|
| `PI_CARD_NUMC` | 카드번호 |
| `PI_FR_DATE` | 조회 시작일 (YYYYMMDD) |
| `PI_TO_DATE` | 조회 종료일 (YYYYMMDD) |
| `PI_STATUS` | 처리 상태 |
| `PI_PERNR_O` | 카드 소유자 사번 |
| `PI_PERNR_R` | 요청자 사번 |
| `PI_CALLSYS` | 호출 시스템 구분 |

### 출력 필드

- `TE_CARD_USE` — 카드 이용내역 테이블
- `TE_CARD_INFO` — 카드 기본정보 테이블

---

## XFI00260 — 비용처리

### 입력 파라미터

| 파라미터 | 설명 |
|----------|------|
| `T_DATA` | 처리 대상 건 배열 (BUKRS, APPR_DATE, CARD_NUMC, APPR_NUMC, DOCPR, PERNR, SGTXT) |

### 출력 필드

| 필드 | 설명 |
|------|------|
| `PE_RESULT` | 처리 결과 (`S`: 성공, `E`: 오류) |
| `PE_MESSAGE` | 결과 메시지 |
| `T_DATA` | 처리 결과 상세 |

---

## XFI00270 — 처리취소

비용처리된 건의 SAP 전표를 취소한다. 입출력 구조는 XFI00260과 유사.

---

## XFI00280 — 업무목록 조회

### 입력

| 파라미터 | 설명 |
|----------|------|
| `PI_BUKRS` | SAP 회사코드 |
| `PI_PERNR` | 사번 |

---

## XFI00290 — 예산 조회

### 입력

| 파라미터 | 설명 |
|----------|------|
| `PI_PERNR` | 사번 |

---

## XFI00310 — 연락처 조회

사번 또는 부서 기준 연락처 정보 조회.

---

## XFI00320 — SAP 공지사항 조회

SAP ERP에 등록된 공지사항을 조회. 입력 파라미터 없음.

---

## _call_sap_soap 내부 구현

```python
def _call_sap_soap(interface_id: str, body_content: str) -> dict:
    soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:urn="urn:sap-com:document:sap:rfc:functions">
      <soapenv:Header/>
      <soapenv:Body>
        {body_content}
      </soapenv:Body>
    </soapenv:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": f'"{interface_id}"',
        "sap-client": "300",
        ...
    }

    response = requests.post(
        SAP_PI_URL,
        data=soap_envelope.encode("utf-8"),
        headers=headers,
        auth=HTTPBasicAuth(SAP_USER, SAP_PASS),
        timeout=30
    )

    root = ET.fromstring(response.content)
    return _parse_xml_to_dict(root)
```

> **주의:** `requests.post`는 동기 IO — FastAPI async 이벤트 루프를 블로킹. 고부하 시 `httpx` 비동기 전환 권장.

---

## 오류 처리 패턴

SAP에서 오류 시 빈 dict `{}` 반환 (예외 전파 없음). 호출부에서 방어 코드 필요:

```python
result = soap_client.call_xfi00250(params)
if not result:
    raise HTTPException(status_code=502, detail="SAP 연동 오류")
```
