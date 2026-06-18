# SAP 인터페이스

## 개요

모든 SAP ERP 연동은 SAP PI(Process Integration)를 통한 SOAP/XML 방식으로 처리됩니다.

| 항목 | 내용 |
|------|------|
| 엔드포인트 | `http://hipop.hhi.co.kr:50000/XISOAPAdapter/MessageServlet` |
| 인증 방식 | HTTP Basic Auth |
| 타임아웃 | 30초 |
| Sender Service | `P_XIMOB` |
| Namespace | `http://hhi.co.kr/FI/XIMOB` |
| 에러 처리 | try/except → 빈 dict `{}` 반환 (예외 전파 없음) |

> ⚠️ SAP 자격증명이 소스코드에 하드코딩되어 있습니다. 환경변수 이관이 필요합니다.

---

## 인터페이스 목록

| ID | 설명 | 호출 위치 | HTTP 메서드 |
|----|------|---------|-----------|
| XFI00250 | 카드 이용내역 / 카드정보 조회 | card_usage.py | GET |
| XFI00260 | 비용처리 (전표 생성) | card_usage.py | POST |
| XFI00270 | 처리취소 (전표 취소) | card_usage.py | POST |
| XFI00280 | 업무목록 조회 | card_usage.py | GET |
| XFI00290 | 예산 조회 | budget.py | GET |
| XFI00310 | 연락처 조회 | contact.py | GET |
| XFI00320 | SAP 공지사항 조회 | notice.py | GET |

---

## 인터페이스 상세

### XFI00250 — 카드 이용내역 조회

**용도**: 법인카드 이용내역 및 카드 정보 조회

**입력 파라미터**:

| 파라미터 | 설명 |
|---------|------|
| PI_CARD_NUMC | 카드 번호 (`"X"` = 카드 정보 조회 모드) |
| PI_FR_DATE | 조회 시작일 (YYYYMMDD) |
| PI_TO_DATE | 조회 종료일 (YYYYMMDD) |
| PI_STATUS | 이용내역 상태 (`A`=전체, 기타 상태 코드) |
| PI_PERNR_O | 요청자 사번 |
| PI_PERNR_R | 조회 대상 사번 (대리 조회 시 다름) |
| PI_CALLSYS | 호출 시스템 (`P` = 운영) |

**응답 필드**:

| 필드 | 설명 |
|------|------|
| TE_CARD_USE | 카드 이용내역 배열 |
| TE_CARD_INFO | 카드 기본 정보 (PI_CARD_NUMC="X" 시) |

---

### XFI00260 — 비용처리 (전표 생성)

**용도**: 선택한 카드 이용내역을 SAP 전표로 생성

**입력 파라미터** (T_DATA 배열):

| 필드 | 설명 |
|------|------|
| BUKRS | 회사 코드 |
| BUDAT | 전표 일자 |
| CARD_NUMC | 카드 번호 |
| APPR_DATE | 승인 일자 |
| APPR_NUMC | 승인 번호 |
| CANC_FLAG | 취소 플래그 |
| SEQN_NUMC | 순번 |
| DOCPR | 업무 코드 |
| PERNR_O | 요청자 사번 |
| PERNR_R | 카드 소지자 사번 |
| SGTXT | 적요 텍스트 |

**응답 필드**:

| 필드 | 설명 |
|------|------|
| PE_RESULT | `S` = 성공, `E` = 오류 |
| PE_MESSAGE | 결과 메시지 |
| T_DATA | 항목별 처리 결과 배열 |

---

### XFI00270 — 처리취소 (전표 취소)

**용도**: 비용처리된 전표 취소

**입력 파라미터** (T_DATA 배열):

| 필드 | 설명 |
|------|------|
| BUKRS | 회사 코드 |
| BELNR | 전표 번호 |
| GJAHR | 회계연도 |
| CARD_NUMC | 카드 번호 |
| APPR_DATE | 승인 일자 |
| APPR_NUMC | 승인 번호 |
| CANC_FLAG | 취소 플래그 |
| SEQN_NUMC | 순번 |
| PERNR | 사번 |

**응답**: XFI00260과 동일 (`PE_RESULT`, `PE_MESSAGE`, `T_DATA`)

---

### XFI00280 — 업무목록 조회

**용도**: 비용처리 팝업의 드롭다운 데이터 (DOCPR, SGTXT 목록)

**입력 파라미터**:

| 파라미터 | 설명 |
|---------|------|
| PI_BUKRS | 회사 코드 |
| PI_PERNR | 사번 |

**응답 필드**:

| 필드 | 설명 |
|------|------|
| TE_TEMPLATE | 업무 템플릿 목록 |
| TE_SGTXT | 적요 텍스트 목록 |
| TE_DOCPR_SGTXT | 업무코드별 적요 목록 |

---

### XFI00290 — 예산 조회

**용도**: 예산 현황 조회

**입력 파라미터**:

| 파라미터 | 설명 |
|---------|------|
| PI_BUKRS | 회사 코드 |
| PI_PERNR | 사번 |
| PI_OBJNR | 오브젝트 번호 |
| PI_OBJTY | 오브젝트 타입 |
| PI_KSTAR | 비용 원소 |
| PI_GJAHR | 회계연도 |
| I_SYSTEM | 시스템 구분 |
| PI_CALLSYS | 호출 시스템 |

> ⚠️ 응답 구조가 동적입니다. 런타임 탐색이 필요하며 키 구조가 미확정입니다.

---

### XFI00310 — 연락처 조회

**용도**: SAP 기반 담당자 연락처 조회

**입력 파라미터**:

| 파라미터 | 설명 |
|---------|------|
| PERNR | 사번 |

> ⚠️ 응답 키가 동적입니다 (`ZFIXT405`, `ET_DATA`, `T_DATA` 중 동적 탐색).

---

### XFI00320 — 공지사항 조회

**용도**: SAP 기반 공지사항 조회 (내부 MSSQL 공지와 병합)

**입력 파라미터**:

| 파라미터 | 설명 |
|---------|------|
| PERNR | 사번 |

**응답 필드**:

| 필드 | 설명 |
|------|------|
| ZFIXT405_1 | 공지사항 배열 |

---

## 공통 SOAP 호출 구조

모든 SAP 호출은 `_call_sap_soap()` 단일 함수를 통합니다.

```python
def _call_sap_soap(interface_id: str, body_content: str) -> Dict:
    url = (
        "http://hipop.hhi.co.kr:50000/XISOAPAdapter/MessageServlet"
        f"?senderService=P_XIMOB"
        f"&interface={interface_id}_LEGY_SO"
        f"&interfaceNamespace={NS}"
    )

    soap_envelope = f"""<soapenv:Envelope xmlns:soapenv="...">
   <soapenv:Header/>
   <soapenv:Body>
      {body_content}
   </soapenv:Body>
</soapenv:Envelope>"""

    try:
        response = requests.post(url, data=soap_envelope.encode('utf-8'),
                                 headers={'Content-Type': 'text/xml;charset=UTF-8'},
                                 auth=HTTPBasicAuth(SAP_USER, SAP_PASS), timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        body = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Body")
        if body is not None and len(body) > 0:
            return _parse_xml_to_dict(body[0])
        return {}
    except Exception as e:
        print(f"[SOAP ERROR] {interface_id}: {e}")
        return {}   # 실패 시 빈 dict 반환
```

---

## XML 요청 Body 패턴

### 단일 파라미터 (XFI00250, XFI00280, XFI00290, XFI00310, XFI00320)

```xml
<ns:MT_XFI00250_LEGY>
    <PI_CARD_NUMC>{card_numc}</PI_CARD_NUMC>
    <PI_FR_DATE>{fr_date}</PI_FR_DATE>
    <PI_TO_DATE>{to_date}</PI_TO_DATE>
    <PI_STATUS>{status}</PI_STATUS>
    <PI_PERNR_O>{pernr_o}</PI_PERNR_O>
    <PI_PERNR_R>{pernr_r}</PI_PERNR_R>
    <PI_CALLSYS>P</PI_CALLSYS>
</ns:MT_XFI00250_LEGY>
```

### 배열 파라미터 (XFI00260, XFI00270)

```xml
<ns:MT_XFI00260_LEGY>
    <T_DATA>
        <BUKRS>{bukrs}</BUKRS>
        <APPR_DATE>{appr_date}</APPR_DATE>
        <CARD_NUMC>{card_numc}</CARD_NUMC>
        ...
    </T_DATA>
    <T_DATA>
        <!-- 다음 항목 -->
    </T_DATA>
</ns:MT_XFI00260_LEGY>
```

---

## PE_RESULT 응답 처리

DML 인터페이스(XFI00260, XFI00270)는 PE_RESULT로 성공 여부를 판단합니다:

```python
result = call_xfi00260(items=t_data)
return {
    "PE_RESULT": result.get("PE_RESULT", ""),      # 'S' = 성공, 'E' = 실패
    "PE_MESSAGE": result.get("PE_MESSAGE", "처리가 완료되었습니다."),
    "T_DATA": result.get("T_DATA", []) or [],
}
```

---

## 주의사항

1. **SAP 자격증명 하드코딩**: `soap_client.py`에 `INFPIUSR/http01`이 평문으로 기재. 환경변수 이관 필요.
2. **동기 블로킹**: `requests.post`는 동기 I/O. async FastAPI 이벤트 루프를 블로킹합니다.
3. **조용한 실패**: 예외 발생 시 빈 dict `{}`를 반환. 호출부에서 빈 결과 방어 처리 필요.
4. **XFI00290, XFI00310 응답 구조**: 키가 동적으로 탐색되므로 SAP 응답이 변경되면 파싱 오류 발생 가능.
