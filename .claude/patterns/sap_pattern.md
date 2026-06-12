# SAP Pattern — MFS SAP SOAP 호출 패턴

추출 시각: 2026-06-11
샘플 파일 수: 1 (core/soap_client.py — 전체 7개 인터페이스)
신뢰도: HIGH (7개 인터페이스 모두 동일 구조)

---

## 올바른 패턴

### 1. 공통 SOAP 호출 함수 — _call_sap_soap() (빈도: 100%, 7/7)

모든 SAP 인터페이스 호출은 `_call_sap_soap(interface_id, body_content)`를 통한다.  
직접 `requests.post`를 호출하지 않는다.

```python
# core/soap_client.py:40-70
def _call_sap_soap(interface_id: str, body_content: str) -> Dict:
    """공통 SOAP 호출 함수"""
    url = (
        "http://hipop.hhi.co.kr:50000/XISOAPAdapter/MessageServlet"
        f"?senderParty=&senderService=P_XIMOB"
        f"&receiverParty=&receiverService="
        f"&interface={interface_id}_LEGY_SO"
        f"&interfaceNamespace={NS}"
    )

    soap_envelope = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="{NS}">
   <soapenv:Header/>
   <soapenv:Body>
      {body_content}
   </soapenv:Body>
</soapenv:Envelope>"""

    try:
        response = requests.post(
            url,
            data=soap_envelope.encode('utf-8'),
            headers={'Content-Type': 'text/xml;charset=UTF-8'},
            auth=HTTPBasicAuth(SAP_USER, SAP_PASS),
            timeout=30
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        body = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Body")
        if body is not None and len(body) > 0:
            return _parse_xml_to_dict(body[0])
        return {}
    except Exception as e:
        print(f"[SOAP ERROR] {interface_id}: {e}")
        return {}   # 실패 시 빈 dict 반환 (예외 전파 안 함)
```

공통 설정 상수:
```python
SAP_USER = "INFPIUSR"
SAP_PASS = "http01"
NS = "http://hhi.co.kr/FI/XIMOB"
```

---

### 2. XML 요청 Body 구성 패턴

#### 2-1. 단일 파라미터 인터페이스 (XFI00250, XFI00280, XFI00290, XFI00310, XFI00320)

루트 태그: `<ns:MT_{인터페이스ID}_LEGY>` 형식. 파라미터는 직접 자식 요소.

```python
# XFI00250 패턴 (단일 파라미터 → 배열 응답)
def call_xfi00250(params: dict) -> Dict:
    inner_xml = f"""<ns:MT_XFI00250_LEGY>
         <PI_CARD_NUMC>{params.get('PI_CARD_NUMC', '')}</PI_CARD_NUMC>
         <PI_FR_DATE>{params.get('PI_FR_DATE', '')}</PI_FR_DATE>
         <PI_TO_DATE>{params.get('PI_TO_DATE', '')}</PI_TO_DATE>
         <PI_STATUS>{params.get('PI_STATUS', 'A')}</PI_STATUS>
         <PI_PERNR_O>{params.get('PI_PERNR_O', '')}</PI_PERNR_O>
         <PI_PERNR_R>{params.get('PI_PERNR_R', '')}</PI_PERNR_R>
         <PI_CALLSYS>{params.get('PI_CALLSYS', 'P')}</PI_CALLSYS>
      </ns:MT_XFI00250_LEGY>"""
    return _call_sap_soap("XFI00250", inner_xml)
```

#### 2-2. 배열 파라미터 인터페이스 (XFI00260, XFI00270) — T_DATA 반복 구조

`<T_DATA>` 요소를 반복하여 배열 전달.

```python
# XFI00260 패턴 (배열 → 처리 결과)
def call_xfi00260(items: list) -> Dict:
    item_xml = ""
    for it in items:
        item_xml += f"""
            <T_DATA>
               <BUKRS>{it.get('BUKRS','')}</BUKRS>
               <BUDAT>{it.get('BUDAT','')}</BUDAT>
               <CARD_NUMC>{it.get('CARD_NUMC','')}</CARD_NUMC>
               <APPR_DATE>{it.get('APPR_DATE','')}</APPR_DATE>
               <APPR_NUMC>{it.get('APPR_NUMC','')}</APPR_NUMC>
               <CANC_FLAG>{it.get('CANC_FLAG','')}</CANC_FLAG>
               <SEQN_NUMC>{it.get('SEQN_NUMC','')}</SEQN_NUMC>
               <DOCPR>{it.get('DOCPR','')}</DOCPR>
               <PERNR_O>{it.get('PERNR_O','')}</PERNR_O>
               <PERNR_R>{it.get('PERNR_R','')}</PERNR_R>
               <SGTXT>{it.get('SGTXT','')}</SGTXT>
               <MSG_TYPE></MSG_TYPE>
               <MSG_TXT></MSG_TXT>
            </T_DATA>"""
    inner_xml = f"<ns:MT_XFI00260_LEGY>{item_xml}</ns:MT_XFI00260_LEGY>"
    return _call_sap_soap("XFI00260", inner_xml)
```

---

### 3. XML 응답 파싱 — _parse_xml_to_dict() (빈도: 100%)

모든 SAP 응답은 `_parse_xml_to_dict()`로 파싱하여 Python dict/list 반환.

```python
def _parse_xml_to_dict(element: ET.Element) -> Any:
    children = list(element)
    if not children:
        return element.text if element.text else ""

    # 동일 태그 여러 개 → 리스트 처리 (배열 응답)
    if len(children) > 1 and len(set(c.tag for c in children)) == 1:
        return [_parse_xml_to_dict(c) for c in children]

    # 혼합 태그 → 딕셔너리 처리
    res = {}
    for child in children:
        tag = child.tag
        if "}" in tag:
            tag = tag.split("}")[1]   # 네임스페이스 제거
        parsed_val = _parse_xml_to_dict(child)
        if tag in res:
            if not isinstance(res[tag], list):
                res[tag] = [res[tag]]
            res[tag].append(parsed_val)
        else:
            res[tag] = parsed_val
    return res
```

---

### 4. SAP 처리 결과 체크 패턴 — PE_RESULT (빈도: 해당 인터페이스 100%)

XFI00260/270처럼 DML 성격의 인터페이스는 `PE_RESULT`로 성공/실패 구분.  
API 엔드포인트에서 이를 그대로 프론트에 전달하여 UI에서 판단.

```python
# card_usage.py:176-183
result = call_xfi00260(items=t_data)
return {
    "PE_RESULT": result.get("PE_RESULT", ""),       # 'S' = 성공, 'E' = 실패
    "PE_MESSAGE": result.get("PE_MESSAGE", "처리가 완료되었습니다."),
    "T_DATA": result.get("T_DATA", []) or [],        # 항목별 처리 결과
}
```

PE_RESULT 값:
- `'S'` — Success (성공)
- `'E'` — Error (실패)

---

### 5. SAP 배열 응답 접근 패턴

각 인터페이스의 응답 키:

| 인터페이스 | 응답 배열 키 | 비고 |
|-----------|------------|------|
| XFI00250 | `TE_CARD_USE`, `TE_CARD_INFO` | PI_CARD_NUMC="X" 시 카드 정보 반환 |
| XFI00260 | `T_DATA`, `PE_RESULT`, `PE_MESSAGE` | 항목별 처리 결과 |
| XFI00270 | `T_DATA`, `PE_RESULT`, `PE_MESSAGE` | 항목별 취소 결과 |
| XFI00280 | `TE_TEMPLATE`, `TE_SGTXT`, `TE_DOCPR_SGTXT` | 드롭다운 데이터 |
| XFI00290 | 동적 구조 | 런타임 탐색 필요 |
| XFI00310 | 동적 구조 | 응답 키 동적 탐색 |
| XFI00320 | `ZFIXT405_1` | 공지사항 배열 |

```python
# 배열 응답 안전 접근 패턴 (card_usage.py)
result = call_xfi00250(params)
rows = result.get('TE_CARD_USE', [])

# None 방어 — "or []" 패턴 (card_usage.py:127-129)
return {
    "TE_TEMPLATE": result.get("TE_TEMPLATE", []) or [],   # None도 []로 변환
    "TE_SGTXT": result.get("TE_SGTXT", []) or [],
}
```

---

### 6. 신규 SAP 인터페이스 추가 패턴

```python
def call_xfi{번호}(params: dict) -> Dict:
    """[인터페이스 설명]"""
    inner_xml = f"""<ns:MT_XFI{번호}_LEGY>
         <PI_{파라미터1}>{params.get('PI_{파라미터1}', '')}</PI_{파라미터1}>
         <PI_{파라미터2}>{params.get('PI_{파라미터2}', '')}</PI_{파라미터2}>
      </ns:MT_XFI{번호}_LEGY>"""
    return _call_sap_soap("XFI{번호}", inner_xml)
```

배열 파라미터가 있는 경우 XFI00260/270의 T_DATA 반복 구조 참조.

---

## 안티패턴 (하지 말 것)

### A1. 자격증명 하드코딩 (soap_client.py:8-9)

```python
# 현재 코드 — 소스에 하드코딩 (보안 이슈)
SAP_USER = "INFPIUSR"
SAP_PASS = "http01"

# 권장 방식 — 환경변수 또는 settings 사용
from app.core.config import settings
SAP_USER = settings.SAP_USER
SAP_PASS = settings.SAP_PASS
```

위험도: MEDIUM — 소스 코드 유출 시 SAP 인증 정보 노출.

---

### A2. _call_sap_soap 실패 시 빈 dict 반환 (조용한 실패)

```python
# 현재 패턴 — 예외 발생해도 빈 dict 반환
except Exception as e:
    print(f"[SOAP ERROR] {interface_id}: {e}")
    return {}   # 호출부에서 실패 여부를 구분할 수 없음
```

호출부에서 `result` 가 `{}` 인지 확인하거나 `PE_RESULT` 를 체크해야 함.  
SAP 장애 시 프론트에 빈 데이터가 표시될 수 있으므로 중요 인터페이스는 호출부에서 빈 결과 방어 처리 필요.

---

### A3. 동적 응답 키 미검증 접근 (notice.py)

```python
# XFI00320 응답 구조가 동적 — 키 존재 여부 확인 필수
result = call_xfi00320(params)
if result and isinstance(result, dict) and "ZFIXT405_1" in result:
    sap_notices = result["ZFIXT405_1"] or []
# 키 없이 직접 접근하면 KeyError
sap_notices = result["ZFIXT405_1"]  # 위험
```

---

## 실제 코드 샘플

- `backend/app/core/soap_client.py:1-11` — 공통 설정 상수
- `backend/app/core/soap_client.py:12-38` — _parse_xml_to_dict() 재귀 파서
- `backend/app/core/soap_client.py:40-70` — _call_sap_soap() 공통 호출 함수
- `backend/app/core/soap_client.py:72-83` — XFI00250 단일 파라미터 패턴
- `backend/app/core/soap_client.py:85-107` — XFI00260 T_DATA 배열 직렬화 패턴
- `backend/app/core/soap_client.py:109-128` — XFI00270 패턴 (XFI00260 변형)
- `backend/app/api/card_usage.py:175-183` — PE_RESULT 응답 처리 패턴
- `backend/app/api/notice.py:32-38` — 동적 응답 키 방어 접근 패턴

---

## 신규 SAP 인터페이스 작성 가이드

1. `backend/app/core/soap_client.py` 하단에 `call_xfi{번호}()` 함수 추가
2. 파라미터 입력 방식 결정: 단일 파라미터(`params: dict`) vs 배열(`items: list`)
3. XML body 구성: `<ns:MT_XFI{번호}_LEGY>` 루트 태그 + `params.get()` 기본값 처리
4. 배열 입력 시: `for it in items: item_xml += "<T_DATA>...</T_DATA>"` 반복
5. `_call_sap_soap("XFI{번호}", inner_xml)` 호출 후 반환
6. API 엔드포인트에서 `result.get('키', []) or []` 방어 패턴으로 응답 처리
7. DML 인터페이스는 `result.get("PE_RESULT", "")` 로 성공/실패 판단 후 반환
